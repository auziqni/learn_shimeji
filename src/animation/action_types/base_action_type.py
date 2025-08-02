#!/usr/bin/env python3
"""
src/animation/action_types/base_action_type.py - Base Action Type

Base class for all animation action types.
Provides consistent interface for action management.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseActionType(ABC):
    """
    Base class for all animation action types.
    
    Provides consistent interface for:
    - Action lifecycle management (start, update, stop)
    - State tracking and transitions
    - Resource management
    - Performance monitoring
    """
    
    def __init__(self, manager):
        """
        Initialize base action type.
        
        Args:
            manager: AnimationManager instance for resource access
        """
        self.manager = manager
        self.action_name = self.__class__.__name__
        self.is_active = False
        self.current_pet_id = None
        self.start_time = None
        self.duration = 0.0
        self.loop_count = 0
        self.max_loops = -1  # -1 = infinite loops
        
        # Performance tracking
        self.total_runtime = 0.0
        self.frame_count = 0
        
        # State management
        self.state_data: Dict[str, Any] = {}
    
    @abstractmethod
    def start(self, pet_id: str) -> bool:
        """
        Start action for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            True if action started successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, pet_id: str, delta_time: float):
        """
        Update action state for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            delta_time: Time since last update in seconds
        """
        pass
    
    @abstractmethod
    def stop(self, pet_id: str):
        """
        Stop action for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
        """
        pass
    
    def get_action_name(self) -> str:
        """Get action type name."""
        return self.action_name
    
    def is_finished(self) -> bool:
        """
        Check if action has finished.
        
        Returns:
            True if action is finished, False otherwise
        """
        if self.max_loops == -1:  # Infinite loops
            return False
        
        return self.loop_count >= self.max_loops
    
    def is_active_for_pet(self, pet_id: str) -> bool:
        """
        Check if action is active for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            True if action is active for pet, False otherwise
        """
        return self.is_active and self.current_pet_id == pet_id
    
    def get_current_pet_id(self) -> Optional[str]:
        """Get current pet ID this action is running for."""
        return self.current_pet_id
    
    def get_runtime(self) -> float:
        """Get total runtime of this action."""
        return self.total_runtime
    
    def get_frame_count(self) -> int:
        """Get total frame count processed."""
        return self.frame_count
    
    def set_duration(self, duration: float):
        """
        Set action duration.
        
        Args:
            duration: Duration in seconds
        """
        self.duration = max(0.0, duration)
    
    def set_loop_count(self, max_loops: int):
        """
        Set maximum loop count.
        
        Args:
            max_loops: Maximum number of loops (-1 for infinite)
        """
        self.max_loops = max_loops
    
    def get_state_data(self) -> Dict[str, Any]:
        """Get current state data."""
        return self.state_data.copy()
    
    def set_state_data(self, key: str, value: Any):
        """
        Set state data.
        
        Args:
            key: State key
            value: State value
        """
        self.state_data[key] = value
    
    def get_state_data_value(self, key: str, default: Any = None) -> Any:
        """
        Get state data value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self.state_data.get(key, default)
    
    def cleanup(self):
        """Clean up action resources."""
        self.is_active = False
        self.current_pet_id = None
        self.start_time = None
        self.total_runtime = 0.0
        self.frame_count = 0
        self.state_data.clear()
    
    def _update_performance_stats(self, delta_time: float):
        """
        Update performance statistics.
        
        Args:
            delta_time: Time since last update
        """
        self.total_runtime += delta_time
        self.frame_count += 1
    
    def _start_action_tracking(self, pet_id: str):
        """
        Start action tracking for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
        """
        self.is_active = True
        self.current_pet_id = pet_id
        self.start_time = self.manager.get_current_time() if hasattr(self.manager, 'get_current_time') else 0.0
        self.loop_count = 0
    
    def _stop_action_tracking(self):
        """Stop action tracking."""
        self.is_active = False
        self.current_pet_id = None
        self.start_time = None
    
    def _increment_loop_count(self):
        """Increment loop count."""
        self.loop_count += 1 