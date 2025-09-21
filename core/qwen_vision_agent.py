import base64
import requests
import re
import os
from PIL import Image
import io
from typing import Tuple, Optional


class QwenVisionAgent:
    """Handles Qwen vision model processing for UI understanding"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_endpoint = "https://router.huggingface.co/v1/chat/completions"
        self.model_name = "Qwen/Qwen2.5-VL-32B-Instruct"
    
    def compress_and_encode_image(self, image_file_path: str, max_dimension: int = 1024, jpeg_quality: int = 85) -> tuple:
        """Compress image and return base64 encoded data with scaling factors"""
        try:
            # Load and process image
            original_image = Image.open(image_file_path)
            original_dimensions = original_image.size  # (width, height)
            rgb_image = original_image.convert("RGB")  # Ensure JPEG compatibility

            # Resize while maintaining aspect ratio
            rgb_image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
            compressed_dimensions = rgb_image.size  # (width, height)

            # Calculate coordinate scaling factors
            width_scale_factor = original_dimensions[0] / compressed_dimensions[0] if compressed_dimensions[0] > 0 else 1.0
            height_scale_factor = original_dimensions[1] / compressed_dimensions[1] if compressed_dimensions[1] > 0 else 1.0

            # Encode to base64
            image_buffer = io.BytesIO()
            rgb_image.save(image_buffer, format="JPEG", quality=jpeg_quality)
            encoded_image_data = base64.b64encode(image_buffer.getvalue()).decode("utf-8")

            return encoded_image_data, width_scale_factor, height_scale_factor

        except Exception as e:
            print(f"Image processing failed: {e}")
            return None, 1.0, 1.0

    def query_qwen_vision_model(self, image_file_path: str, user_prompt: str) -> tuple:
        """Query Qwen vision model with image and prompt"""
        if not image_file_path or not os.path.exists(image_file_path):
            return None, 1.0, 1.0

        # Process image
        processing_result = self.compress_and_encode_image(image_file_path)
        if processing_result[0] is None:
            return None, 1.0, 1.0

        encoded_image_data, width_scale_factor, height_scale_factor = processing_result

        try:
            request_headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

            request_payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image_data}"}
                            }
                        ]
                    }
                ],
                "model": self.model_name,
                "max_tokens": 300,
                "temperature": 0.2
            }

            api_response = requests.post(self.api_endpoint, headers=request_headers, json=request_payload, timeout=35)

            if api_response.status_code == 200:
                response_data = api_response.json()
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    model_response = response_data["choices"][0]["message"]["content"]
                    return model_response.strip(), width_scale_factor, height_scale_factor
                else:
                    print(f"No response choices from Qwen model")
                    return None, 1.0, 1.0
            else:
                print(f"API error: {api_response.status_code} - {api_response.text}")
                return None, 1.0, 1.0

        except requests.exceptions.Timeout:
            print(f"Qwen model request timeout")
            return None, 1.0, 1.0
        except Exception as e:
            print(f"Qwen model error: {e}")
            return None, 1.0, 1.0

    def extract_action_from_response(self, model_response: str, width_scale_factor: float, height_scale_factor: float) -> Optional[str]:
        """Parse action command from model response and scale coordinates"""
        response_lines = model_response.strip().split('\n')

        # Look for valid action patterns
        for line in response_lines:
            line = line.strip()

            # Skip empty lines and markdown
            if not line or line.startswith('#') or line.startswith('```'):
                continue

            # Parse TAP actions and scale coordinates
            tap_pattern = re.search(r'TAP\s*\((\d+),\s*(\d+)\)', line)
            if tap_pattern:
                original_x, original_y = int(tap_pattern.group(1)), int(tap_pattern.group(2))
                scaled_x = int(original_x * width_scale_factor)
                scaled_y = int(original_y * height_scale_factor)
                comment_text = line.split('#', 1)[1].strip() if '#' in line else "scaled coordinates"
                return f"TAP ({scaled_x},{scaled_y}) # {comment_text}"

            elif re.search(r"TYPE\s*['\"]", line):
                return line
            elif 'SCROLL' in line.upper():
                return line
            elif 'TASK_COMPLETE' in line.upper():
                return line

        # Fallback parsing from full response
        full_response_text = model_response.strip()

        # Extract and scale TAP coordinates
        tap_pattern = re.search(r'TAP\s*\((\d+),\s*(\d+)\)', full_response_text)
        if tap_pattern:
            original_x, original_y = int(tap_pattern.group(1)), int(tap_pattern.group(2))
            scaled_x = int(original_x * width_scale_factor)
            scaled_y = int(original_y * height_scale_factor)
            return f"TAP ({scaled_x},{scaled_y}) # extracted and scaled"

        # Extract TYPE commands
        type_pattern = re.search(r"TYPE\s*['\"]([^'\"]+)['\"]", full_response_text)
        if type_pattern:
            return f"TYPE '{type_pattern.group(1)}' # extracted action"

        # Extract SCROLL commands
        if 'SCROLL' in full_response_text.upper():
            return "SCROLL down # extracted action"

        # Extract completion signals
        if 'TASK_COMPLETE' in full_response_text.upper():
            return "TASK_COMPLETE: extracted from response"

        return None

    def generate_context_aware_prompt(self, task_instruction: str, current_step: int, search_initiated: bool, query_entered: bool) -> str:
        """Generate context-aware prompts based on task progress"""
        task_header = f"Task: {task_instruction}\nStep: {current_step}/15\n\n"

        if not search_initiated:
            return task_header + """
CRITICAL: Respond with ONLY ONE action line in the exact format shown below.

Locate the search bar or search icon on this screen.

RESPOND WITH EXACTLY ONE OF THESE:
TAP (x,y) # Search bar
TAP (x,y) # Search icon  
SCROLL down # to find search

Do NOT provide explanations. Only respond with the action line.
"""

        elif not query_entered:
            return task_header + """
CRITICAL: Respond with ONLY ONE action line in the exact format shown below.

Look for a text input field or search box where you can type.

RESPOND WITH EXACTLY ONE OF THESE:
TYPE 'headphones under 1000' # search query
TAP (x,y) # search input field
SCROLL down # to find input

Do NOT provide explanations. Only respond with the action line.
"""

        else:
            return task_header + """
CRITICAL: Respond with ONLY ONE action line in the exact format shown below.

Look for search results or product filters.

RESPOND WITH EXACTLY ONE OF THESE:
TAP (x,y) # product or filter
SCROLL down # see more results
TASK_COMPLETE: Found relevant products

Do NOT provide explanations. Only respond with the action line.
""" 