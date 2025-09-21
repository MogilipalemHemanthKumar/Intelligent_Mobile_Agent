import hashlib
import os
from typing import Dict, List


class AppUtilities:
    """Utility functions for the mobile automation agent"""
    
    @staticmethod
    def calculate_screen_hash(image_file_path: str) -> str:
        """Generate MD5 hash for screen image to detect loops"""
        try:
            with open(image_file_path, 'rb') as image_file:
                return hashlib.md5(image_file.read()).hexdigest()
        except:
            return ""
    
    @staticmethod
    def extract_app_identifier(task_instruction: str) -> str:
        """Extract target app name from task instruction"""
        instruction_text = task_instruction.lower()
        supported_apps = {
            'flipkart': 'flipkart', 
            'amazon': 'amazon', 
            'blinkit': 'blinkit',
            'zomato': 'zomato', 
            'ola': 'ola'
        }

        for app_keyword in supported_apps:
            if app_keyword in instruction_text:
                return supported_apps[app_keyword]
        return 'unknown'
    
    @staticmethod
    def get_app_package_name(app_identifier: str) -> str:
        """Get Android package name for app identifier"""
        package_mapping = {
            'flipkart': 'com.flipkart.android',
            'amazon': 'in.amazon.mShop.android.shopping',
            'blinkit': 'com.grofers.customerapp',
            'zomato': 'com.application.zomata',
            'ola': 'com.olacabs.customer'
        }
        
        return package_mapping.get(app_identifier.lower(), app_identifier)
    
    @staticmethod
    def get_predefined_fallback_actions() -> List[str]:
        """Get list of predefined fallback actions"""
        return [
            "TAP (540,150)",  # Top center area
            "SCROLL down",    # Scroll down
            "TAP (100,300)",  # Left side area
            "TAP (540,400)"   # Center area
        ]
    
    @staticmethod
    def ensure_directory_structure(screenshot_directory: str, ui_dump_directory: str):
        """Create necessary directories for file storage"""
        os.makedirs(screenshot_directory, exist_ok=True)
        os.makedirs(ui_dump_directory, exist_ok=True)
    
    @staticmethod
    def validate_coordinate_range(x_coord: int, y_coord: int, max_x: int = 1080, max_y: int = 1920) -> bool:
        """Validate if coordinates are within acceptable device bounds"""
        return 0 <= x_coord <= max_x and 0 <= y_coord <= max_y 