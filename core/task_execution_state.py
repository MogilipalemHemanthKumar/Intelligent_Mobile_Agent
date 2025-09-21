from typing import List


class TaskExecutionState:
    """Manages execution state and progress tracking"""
    
    def __init__(self, maximum_steps: int = 25):
        # Task execution context
        self.active_task_description = ""
        self.current_step_number = 0
        self.maximum_allowed_steps = maximum_steps
        
        # Task progress indicators
        self.search_initiated = False
        self.query_entered = False
        
        # Loop detection mechanism
        self.screen_hash_history = []
        
    def initialize_new_task(self, task_description: str):
        """Initialize state for new task execution"""
        self.active_task_description = task_description
        self.current_step_number = 0
        self.search_initiated = False
        self.query_entered = False
        self.screen_hash_history = []
    
    def advance_step_counter(self):
        """Increment the current step number"""
        self.current_step_number += 1
    
    def has_reached_step_limit(self) -> bool:
        """Check if maximum steps have been reached"""
        return self.current_step_number >= self.maximum_allowed_steps
    
    def record_screen_hash(self, screen_hash: str):
        """Record screen hash for loop detection"""
        self.screen_hash_history.append(screen_hash)
        # Keep only recent hashes for efficiency
        self.screen_hash_history = self.screen_hash_history[-5:]
    
    def detect_screen_loop(self, current_screen_hash: str) -> bool:
        """Detect if we're stuck in a screen loop"""
        return current_screen_hash in self.screen_hash_history[-3:]  # Same screen appeared 3 times
    
    def update_task_progress(self, executed_action: str):
        """Update task progress based on executed action"""
        if 'TAP' in executed_action and any(search_keyword in executed_action.lower() 
                                          for search_keyword in ['search', 'input', 'field', 'box', 'bar']):
            self.search_initiated = True
        elif 'TYPE' in executed_action:
            self.query_entered = True 