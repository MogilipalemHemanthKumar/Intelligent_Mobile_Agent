#!/usr/bin/env python3
"""
Configuration management for Intelligent Mobile Agent
Simplified for Qwen vision model only
"""

import os
from typing import Optional


def load_environment_variables(env_file_path: str = '.env') -> None:
    """Load environment variables from configuration file"""
    if not os.path.exists(env_file_path):
        print(f"Configuration file {env_file_path} not found. Using default settings.")
        return

    try:
        with open(env_file_path, 'r') as config_file:
            for config_line in config_file:
                config_line = config_line.strip()
                if config_line and not config_line.startswith('#') and '=' in config_line:
                    config_key, config_value = config_line.split('=', 1)
                    os.environ[config_key.strip()] = config_value.strip()
    except Exception as e:
        print(f"Error loading configuration from {env_file_path}: {e}")


class AgentConfiguration:
    """Configuration class for Intelligent Mobile Agent"""

    def __init__(self):
        # Load environment variables
        load_environment_variables()

        # Hugging Face API configuration
        self.huggingface_api_token = os.getenv('HUGGINGFACE_API_TOKEN', '')
        if not self.huggingface_api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables. Please set it in .env file.")

        # Android device configuration
        self.target_android_device_id = os.getenv('TARGET_ANDROID_DEVICE_ID', None)

        # Agent execution parameters
        self.maximum_steps = int(os.getenv('MAXIMUM_EXECUTION_STEPS', '20'))
        self.maximum_action_repetitions = int(os.getenv('MAXIMUM_ACTION_REPETITIONS', '3'))
        self.screenshot_compression_quality = int(os.getenv('SCREENSHOT_COMPRESSION_QUALITY', '95'))

        # Qwen vision model configuration
        self.qwen_model_name = "Qwen/Qwen2.5-VL-32B-Instruct"

        # System operation mode
        self.debug_logging_enabled = os.getenv('DEBUG_LOGGING_ENABLED', 'false').lower() == 'true'

        # File storage directories
        self.screenshot_storage_directory = "device_screenshots"
        self.ui_hierarchy_storage_directory = "ui_hierarchy_dumps"

    def validate_configuration(self) -> bool:
        """Validate agent configuration parameters"""
        if not self.huggingface_api_token or self.huggingface_api_token == 'your_hugging_face_api_key_here':
            print("Invalid HUGGINGFACE_API_TOKEN. Please update your .env file with a valid Hugging Face API key.")
            return False

        if self.maximum_steps < 1 or self.maximum_steps > 50:
            print("MAXIMUM_EXECUTION_STEPS should be between 1 and 50")
            return False
        return True

    def display_configuration_summary(self) -> None:
        """Display current configuration summary (hiding sensitive data)"""
        print("\n🔧 Agent Configuration Summary:")
        print(f"   HF API Token: {'Set' if self.huggingface_api_token else '❌ Missing'}")
        print(f"   Target Device: {self.target_android_device_id or 'Auto-detect'}")
        print(f"   Maximum Steps: {self.maximum_steps}")
        print(f"   Max Action Repetitions: {self.maximum_action_repetitions}")
        print(f"   Screenshot Quality: {self.screenshot_compression_quality}")
        print(f"   Vision Model: {self.qwen_model_name}")
        print(f"   Debug Logging: {self.debug_logging_enabled}")
        print(f"   Screenshot Directory: {self.screenshot_storage_directory}")
        print(f"   UI Hierarchy Directory: {self.ui_hierarchy_storage_directory}")


# Global configuration instance
agent_configuration_instance = None


def get_agent_configuration() -> AgentConfiguration:
    """Get global agent configuration instance"""
    global agent_configuration_instance
    if agent_configuration_instance is None:
        agent_configuration_instance = AgentConfiguration()
        if not agent_configuration_instance.validate_configuration():
            raise ValueError("Agent configuration validation failed")
    return agent_configuration_instance 
