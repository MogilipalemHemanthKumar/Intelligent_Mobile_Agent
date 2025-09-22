import os
import re
import time
from typing import Tuple, Optional
from agent_config import get_agent_configuration

# Import core modules
from core.android_controller import AndroidController
from core.qwen_vision_agent import QwenVisionAgent
from core.ui_element_parser import UIElementParser
from core.action_coordinator import ActionCoordinator
from core.app_utilities import AppUtilities
from core.task_execution_state import TaskExecutionState


class IntelligentMobileAgent:
    """AI-powered mobile automation agent using Qwen vision model"""
    
    def __init__(self):
        # Load system configuration
        self.agent_config = get_agent_configuration()
        
        # Initialize execution state manager
        self.execution_state = TaskExecutionState(maximum_steps=self.agent_config.maximum_steps)
        
        # Setup file storage directories
        self.screenshot_storage_dir = "device_screenshots"
        self.ui_hierarchy_storage_dir = "ui_hierarchy_dumps"
        AppUtilities.ensure_directory_structure(self.screenshot_storage_dir, self.ui_hierarchy_storage_dir)
        
        # Initialize core components
        self.android_controller = AndroidController()
        self.qwen_vision_agent = QwenVisionAgent(api_token=self.agent_config.huggingface_api_token)
        self.ui_element_parser = UIElementParser()
        self.action_coordinator = ActionCoordinator(self.android_controller)
        print("#" * 60)
        print("Intelligent Mobile Agent with Qwen Vision Ready!")
        print("#" * 60)
    def capture_device_state(self) -> Tuple[str, str]:
        """Capture current device screen and UI hierarchy"""
        self.execution_state.advance_step_counter()
        screenshot_file_path = f"{self.screenshot_storage_dir}/step_{self.execution_state.current_step_number:02d}.png"
        ui_hierarchy_file_path = f"{self.ui_hierarchy_storage_dir}/step_{self.execution_state.current_step_number:02d}.xml"
        
        # Capture device screenshot
        screenshot_captured = self.android_controller.capture_device_screenshot(screenshot_file_path)
        
        # Capture UI hierarchy
        ui_hierarchy_captured = self.android_controller.capture_ui_hierarchy(ui_hierarchy_file_path)
        
        return (screenshot_file_path if screenshot_captured else None,
                ui_hierarchy_file_path if ui_hierarchy_captured else None)
    
    def execute_task_instruction(self, task_instruction: str) -> str:
        """Execute mobile automation task based on natural language instruction"""
        print(f"\nTask: {task_instruction}")
       
        
        # Initialize task execution state
        self.execution_state.initialize_new_task(task_instruction)
        self.action_coordinator.reset_action_history()
        
        # Identify and launch target application
        app_identifier = AppUtilities.extract_app_identifier(task_instruction)
        
        if app_identifier != "unknown":
            app_package_name = AppUtilities.get_app_package_name(app_identifier)
            if not self.android_controller.launch_application(app_package_name):
                return "Failed to launch target application"
        
        # Main task execution loop
        task_completion_achieved = False
        final_execution_result = ""
        
        while not self.execution_state.has_reached_step_limit() and not task_completion_achieved:
            # Capture current device state
            screenshot_path, ui_hierarchy_path = self.capture_device_state()
            
            # Check for screen navigation loops
            if screenshot_path:
                current_screen_hash = AppUtilities.calculate_screen_hash(screenshot_path)
                if self.execution_state.detect_screen_loop(current_screen_hash):
                    print("Screen loop detected, attempting navigation recovery...")
                    self.android_controller.perform_scroll_action('down')
                    continue
                self.execution_state.record_screen_hash(current_screen_hash)
            
            action_to_execute = None
            
            # Primary: Use Qwen vision model for action planning
            if screenshot_path:
                context_aware_prompt = self.qwen_vision_agent.generate_context_aware_prompt(
                    task_instruction, 
                    self.execution_state.current_step_number,
                    self.execution_state.search_initiated,
                    self.execution_state.query_entered
                )
                qwen_response, width_scale_factor, height_scale_factor = self.qwen_vision_agent.query_qwen_vision_model(
                    screenshot_path, context_aware_prompt
                )
                
                if qwen_response:
                    # Parse and scale action coordinates
                    action_to_execute = self.qwen_vision_agent.extract_action_from_response(
                        qwen_response, width_scale_factor, height_scale_factor
                    )
                    
                    if action_to_execute:
                        # Update execution progress
                        self.execution_state.update_task_progress(action_to_execute)
                        print(f"Action Executed: {action_to_execute}")
            
            # Secondary: Fallback to UI hierarchy analysis
            if not action_to_execute and ui_hierarchy_path:
                print("Using UI hierarchy analysis as fallback")
                parsed_ui_elements = self.ui_element_parser.parse_ui_hierarchy(ui_hierarchy_path)
                
                if not self.execution_state.search_initiated:
                    # Look for search-related elements
                    search_element_candidates = self.ui_element_parser.identify_search_elements(parsed_ui_elements)
                    if search_element_candidates:
                        best_search_element = search_element_candidates[0]
                        action_to_execute = f"TAP ({best_search_element['center_x']},{best_search_element['center_y']}) # Search: {best_search_element['display_text'] or best_search_element['content_description']}"
                        self.execution_state.search_initiated = True
                
                if not action_to_execute:
                    # Generate fallback action from UI elements
                    action_to_execute = self.ui_element_parser.generate_fallback_action(
                        parsed_ui_elements, self.execution_state.current_step_number
                    )
            
            # Tertiary: Use predefined fallback actions
            if not action_to_execute:
                fallback_action_options = AppUtilities.get_predefined_fallback_actions()
                action_to_execute = fallback_action_options[self.execution_state.current_step_number % len(fallback_action_options)]
                print(f"Using predefined fallback: {action_to_execute}")
            
            # Execute the determined action
            task_completion_achieved = self.action_coordinator.execute_parsed_action(action_to_execute)
            
            # Update execution progress
            self.execution_state.update_task_progress(action_to_execute)
            
            # Check for explicit task completion
            if 'TASK_COMPLETE' in action_to_execute:
                completion_match = re.search(r'TASK_COMPLETE:\s*(.+)', action_to_execute)
                final_execution_result = completion_match.group(1) if completion_match else "Task completed successfully"
                break
        
        if not final_execution_result:
            final_execution_result = f"Task completed in {self.execution_state.current_step_number} steps."
        
        print(f"{final_execution_result}")
        print("#" * 60)
        return final_execution_result


def main():
    """Demonstration of intelligent mobile agent capabilities"""
    try:
        mobile_agent = IntelligentMobileAgent()
        demo_task = "Open Blinkit, find watermelons near me at lower cost"
        execution_result = mobile_agent.execute_task_instruction(demo_task)
        
    except Exception as e:
        print(f"Agent initialization failed: {e}")


if __name__ == "__main__":
    main() 
