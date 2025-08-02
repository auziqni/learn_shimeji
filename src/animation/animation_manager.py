#!/usr/bin/env python3
"""
src/animation/animation_manager.py - Central Animation Manager

Central controller for all animation operations.
Integrates sprite loading, JSON parsing, and action type management.
Supports 25+ pets simultaneously with memory optimization.
"""

import time
from typing import Dict, List, Optional, Any
from .sprite_loader import SpriteLoader
from utils.json_parser import JSONParser
from .action_types.stay_animation import StayAnimation


class AnimationManager:
    """
    Central animation manager (MAESTRO).
    
    Features:
    - Centralized sprite loading and caching
    - JSON data parsing and management
    - Action type registration and management
    - Multi-pet animation support
    - Performance monitoring and optimization
    """
    
    def __init__(self, max_cache_size: int = 100, max_memory_mb: float = 50.0):
        """
        Initialize animation manager.
        
        Args:
            max_cache_size: Maximum number of cached sprites
            max_memory_mb: Maximum memory usage in MB
        """
        # Core components
        self.sprite_loader = SpriteLoader(max_cache_size, max_memory_mb)
        self.json_parser = JSONParser()
        
        # Action type registry
        self.action_types: Dict[str, Any] = {}
        self._register_default_action_types()
        
        # Pet management
        self.pets: Dict[str, Dict[str, Any]] = {}  # pet_id -> pet_info
        self.active_actions: Dict[str, Any] = {}  # pet_id -> current_action
        
        # Performance tracking
        self.start_time = time.time()
        self.total_updates = 0
        self.total_pets_managed = 0
        
        # Statistics
        self.action_start_count = 0
        self.action_stop_count = 0
        self.error_count = 0
    
    def _register_default_action_types(self):
        """Register default action types."""
        self.register_action_type("stay", StayAnimation(self))
        print("✅ Registered default action types")
    
    def register_action_type(self, action_name: str, action_type):
        """
        Register an action type.
        
        Args:
            action_name: Name of the action type
            action_type: Action type instance
        """
        self.action_types[action_name] = action_type
        print(f"✅ Registered action type: {action_name}")
    
    def get_action_type(self, action_name: str):
        """
        Get registered action type.
        
        Args:
            action_name: Name of the action type
            
        Returns:
            Action type instance or None if not found
        """
        return self.action_types.get(action_name)
    
    def get_available_action_types(self) -> List[str]:
        """Get list of available action types."""
        return list(self.action_types.keys())
    
    def add_pet(self, pet_id: str, sprite_pack: str = "Hornet", **kwargs):
        """
        Add a pet to the animation manager.
        
        Args:
            pet_id: Unique identifier for the pet
            sprite_pack: Name of the sprite pack
            **kwargs: Additional pet properties
        """
        self.pets[pet_id] = {
            'sprite_pack': sprite_pack,
            'position': kwargs.get('position', (100, 100)),
            'active': True,
            'created_time': time.time(),
            **kwargs
        }
        self.total_pets_managed += 1
        print(f"✅ Added pet {pet_id} with sprite pack {sprite_pack}")
    
    def remove_pet(self, pet_id: str):
        """
        Remove a pet from the animation manager.
        
        Args:
            pet_id: Unique identifier for the pet
        """
        if pet_id in self.pets:
            # Stop any active action
            self.stop_pet_action(pet_id)
            
            # Remove pet
            del self.pets[pet_id]
            print(f"🗑️  Removed pet {pet_id}")
    
    def get_pet_info(self, pet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pet information.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            Pet info dictionary or None if not found
        """
        return self.pets.get(pet_id)
    
    def get_all_pets(self) -> List[str]:
        """Get list of all pet IDs."""
        return list(self.pets.keys())
    
    def start_pet_action(self, pet_id: str, action_name: str) -> bool:
        """
        Start an action for a specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            action_name: Name of the action type
            
        Returns:
            True if action started successfully, False otherwise
        """
        try:
            # Check if pet exists
            if pet_id not in self.pets:
                print(f"❌ Pet {pet_id} not found")
                return False
            
            # Get action type
            action_type = self.get_action_type(action_name)
            if not action_type:
                print(f"❌ Action type {action_name} not found")
                return False
            
            # Stop current action if any
            self.stop_pet_action(pet_id)
            
            # Start new action
            if action_type.start(pet_id):
                self.active_actions[pet_id] = action_type
                self.action_start_count += 1
                print(f"✅ Started {action_name} for pet {pet_id}")
                return True
            else:
                print(f"❌ Failed to start {action_name} for pet {pet_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting action {action_name} for pet {pet_id}: {e}")
            self.error_count += 1
            return False
    
    def stop_pet_action(self, pet_id: str):
        """
        Stop current action for a specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
        """
        if pet_id in self.active_actions:
            action = self.active_actions[pet_id]
            action.stop(pet_id)
            del self.active_actions[pet_id]
            self.action_stop_count += 1
            print(f"🛑 Stopped action for pet {pet_id}")
    
    def update_pet_action(self, pet_id: str, delta_time: float):
        """
        Update action for a specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            delta_time: Time since last update in seconds
        """
        if pet_id in self.active_actions:
            try:
                action = self.active_actions[pet_id]
                action.update(pet_id, delta_time)
                
                # Check if action finished
                if action.is_finished():
                    self.stop_pet_action(pet_id)
                    
            except Exception as e:
                print(f"❌ Error updating action for pet {pet_id}: {e}")
                self.error_count += 1
    
    def update_all_pets(self, delta_time: float):
        """
        Update all active pets.
        
        Args:
            delta_time: Time since last update in seconds
        """
        self.total_updates += 1
        
        for pet_id in list(self.active_actions.keys()):
            self.update_pet_action(pet_id, delta_time)
    
    def get_pet_action(self, pet_id: str):
        """
        Get current action for a specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            Current action instance or None if no active action
        """
        return self.active_actions.get(pet_id)
    
    def get_pet_sprite(self, pet_id: str):
        """
        Get current sprite for a specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            Current sprite or None if no active action
        """
        action = self.get_pet_action(pet_id)
        if action and hasattr(action, 'get_current_sprite'):
            return action.get_current_sprite()
        return None
    
    def get_current_time(self) -> float:
        """Get current time since manager start."""
        return time.time() - self.start_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            'total_pets': len(self.pets),
            'active_pets': len(self.active_actions),
            'total_updates': self.total_updates,
            'total_pets_managed': self.total_pets_managed,
            'action_start_count': self.action_start_count,
            'action_stop_count': self.action_stop_count,
            'error_count': self.error_count,
            'runtime': self.get_current_time(),
            'available_action_types': self.get_available_action_types(),
            'sprite_loader_stats': self.sprite_loader.get_statistics()
        }
    
    def clear_cache(self):
        """Clear sprite cache."""
        self.sprite_loader.clear_cache()
        print("🧹 Cleared animation manager cache")
    
    def cleanup(self):
        """Clean up all resources."""
        # Stop all active actions
        for pet_id in list(self.active_actions.keys()):
            self.stop_pet_action(pet_id)
        
        # Clean up action types
        for action_type in self.action_types.values():
            if hasattr(action_type, 'cleanup'):
                action_type.cleanup()
        
        # Clear caches
        self.clear_cache()
        
        # Reset statistics
        self.pets.clear()
        self.active_actions.clear()
        self.total_updates = 0
        self.total_pets_managed = 0
        self.action_start_count = 0
        self.action_stop_count = 0
        self.error_count = 0
        
        print("🧹 Animation manager cleaned up")
    
    def load_sprite_pack(self, sprite_pack: str) -> bool:
        """
        Load sprite pack data.
        
        Args:
            sprite_pack: Name of the sprite pack
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load sprite pack data via JSON parser
            success = self.json_parser.load_all_sprite_packs()
            if success:
                print(f"✅ Loaded sprite pack data")
                return True
            else:
                print(f"❌ Failed to load sprite pack data")
                return False
                
        except Exception as e:
            print(f"❌ Error loading sprite pack {sprite_pack}: {e}")
            self.error_count += 1
            return False 