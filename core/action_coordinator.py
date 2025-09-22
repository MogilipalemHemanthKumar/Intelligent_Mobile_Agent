import re
import time
from typing import Optional
from .android_controller import AndroidController


class ActionCoordinator:
    """Coordinates action parsing and execution with loop prevention"""
    
    def __init__(self, android_controller: AndroidController):
        self.android_controller = android_controller
        self.executed_actions_history = []
        self.max_action_repetitions = 2
    
    def is_action_repeating(self, action_command: str) -> bool:
        """Check if action is being repeated excessively"""
        # Extract coordinates for comparison
        coordinate_pattern = re.search(r'TAP\s*\((\d+),\s*(\d+)\)', action_command)
        if coordinate_pattern:
            coordinate_string = f"TAP({coordinate_pattern.group(1)},{coordinate_pattern.group(2)})"
            recent_actions = self.executed_actions_history[-4:]  # Check last 4 actions
            return recent_actions.count(coordinate_string) >= self.max_action_repetitions
        return False
    
    def execute_parsed_action(self, action_command: str) -> bool:
        """Parse and execute action with loop prevention"""
        # Clean action text
        cleaned_action = action_command.strip()

        # Extract primary action from multi-line responses
        action_lines = cleaned_action.split('\n')
        for line in action_lines:
            line = line.strip()
            if re.search(r'TAP\s*\(\d+,\s*\d+\)', line):
                cleaned_action = line
                break
            elif re.search(r"TYPE\s*['\"]", line):
                cleaned_action = line
                break
            elif 'SCROLL' in line.upper():
                cleaned_action = line
                break
            elif 'TASK_COMPLETE' in line.upper():
                cleaned_action = line
                break

        # Check for repetitive actions
        coordinate_pattern = re.search(r'TAP\s*\((\d+),\s*(\d+)\)', cleaned_action)
        if coordinate_pattern and self.is_action_repeating(cleaned_action):
            print("Detected repetitive action, applying alternative strategy...")
            # Use scroll as alternative
            self.android_controller.perform_scroll_action('down')
            return False

        # Track action for loop detection
        if coordinate_pattern:
            coordinate_string = f"TAP({coordinate_pattern.group(1)},{coordinate_pattern.group(2)})"
            self.executed_actions_history.append(coordinate_string)
            # Maintain sliding window of recent actions
            self.executed_actions_history = self.executed_actions_history[-10:]

        # Execute TAP actions
        if coordinate_pattern:
            x_coord, y_coord = int(coordinate_pattern.group(1)), int(coordinate_pattern.group(2))
            self.android_controller.perform_tap_action(x_coord, y_coord)
            return False

        # Execute TYPE actions
        type_pattern = re.search(r"TYPE\s*['\"]([^'\"]+)['\"]", cleaned_action)
        if type_pattern:
            input_text = type_pattern.group(1)
            self.android_controller.perform_text_input(input_text)
            return False

        # Execute SCROLL actions
        if 'SCROLL' in cleaned_action.upper():
            scroll_direction = 'up' if 'up' in cleaned_action.lower() else 'down'
            self.android_controller.perform_scroll_action(scroll_direction)
            return False

        # Handle task completion
        if 'TASK_COMPLETE' in cleaned_action.upper():
            return True

        return False
    
    def reset_action_history(self):
        """Reset action history for new task"""
        self.executed_actions_history = [] 
