#!/usr/bin/env python3
"""
src/animation/action_types/stay_animation.py - Stay Animation Action Type

Handles static animations where the pet stays in place.
Supports sound effects and looping animations.
"""

import time
from typing import Optional, List, Dict, Any
from .base_action_type import BaseActionType


class StayAnimation(BaseActionType):
    """
    Stay animation action type.
    
    Handles static animations where the pet stays in place.
    Features:
    - Static position animation
    - Sound support
    - Looping animations
    - Performance tracking
    """
    
    def __init__(self, manager):
        """
        Initialize stay animation.
        
        Args:
            manager: AnimationManager instance
        """
        super().__init__(manager)
        self.action_name = "StayAnimation"
        
        # Animation state
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.frames_data = []
        self.sprite_pack_path = ""
        
        # Sound state
        self.sound_enabled = True
        self.last_played_sound = None
        self.sound_volume = 1.0
        
        # Animation settings
        self.frame_duration = 1.0 / 30.0  # 30 FPS default
        self.is_looping = True
        
        # Performance tracking
        self.sprite_load_count = 0
        self.sound_play_count = 0
    
    def start(self, pet_id: str) -> bool:
        """
        Start stay animation for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            True if animation started successfully, False otherwise
        """
        try:
            # Start action tracking
            self._start_action_tracking(pet_id)
            
            # Reset animation state
            self.current_frame_index = 0
            self.frame_timer = 0.0
            
            # Load animation data if not already loaded
            if not self.frames_data:
                if not self._load_animation_data(pet_id):
                    return False
            
            print(f"✅ Started stay animation for pet {pet_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting stay animation for pet {pet_id}: {e}")
            return False
    
    def update(self, pet_id: str, delta_time: float):
        """
        Update stay animation for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
            delta_time: Time since last update in seconds
        """
        if not self.is_active_for_pet(pet_id):
            return
        
        try:
            # Update performance stats
            self._update_performance_stats(delta_time)
            
            # Update frame timer
            self.frame_timer += delta_time
            
            # Check if it's time to move to next frame
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0.0
                
                # Play sound for current frame
                self._play_frame_sound()
                
                # Move to next frame
                self.current_frame_index += 1
                
                # Handle looping
                if self.current_frame_index >= len(self.frames_data):
                    if self.is_looping:
                        self.current_frame_index = 0
                        self._increment_loop_count()
                    else:
                        self.stop(pet_id)
            
        except Exception as e:
            print(f"❌ Error updating stay animation for pet {pet_id}: {e}")
    
    def stop(self, pet_id: str):
        """
        Stop stay animation for specific pet.
        
        Args:
            pet_id: Unique identifier for the pet
        """
        if self.is_active_for_pet(pet_id):
            self._stop_action_tracking()
            print(f"🛑 Stopped stay animation for pet {pet_id}")
    
    def _load_animation_data(self, pet_id: str) -> bool:
        """
        Load animation data for the pet.
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            # Get pet's sprite pack info from manager
            pet_info = self.manager.get_pet_info(pet_id)
            if not pet_info:
                print(f"⚠️  No pet info found for {pet_id}")
                return False
            
            sprite_pack = pet_info.get('sprite_pack', 'Hornet')
            self.sprite_pack_path = f"assets/{sprite_pack}"
            
            # Load stay animation data from JSON parser
            actions = self.manager.json_parser.get_actions(sprite_pack)
            if not actions:
                print(f"⚠️  No actions found for sprite pack {sprite_pack}")
                return False
            
            # Find stay-related actions or actions with animation blocks
            stay_actions = []
            for action_name, action_data in actions.items():
                # Check if it's a stay action or has animation blocks
                if ('stay' in action_name.lower() or 'idle' in action_name.lower() or 
                    action_name.lower() == 'stand' or
                    (action_data.animation_blocks or action_data.default_animation)):
                    stay_actions.append((action_name, action_data))
            
            # If no stay actions found, use first action with animation blocks
            if not stay_actions:
                print(f"⚠️  No stay actions found for sprite pack {sprite_pack}, using first available action")
                if actions:
                    action_name = list(actions.keys())[0]
                    action_data = actions[action_name]
                    stay_actions.append((action_name, action_data))
                else:
                    print(f"❌ No actions available for sprite pack {sprite_pack}")
                    return False
            
            # Use first action found
            action_name, action_data = stay_actions[0]
            
            # Get animation blocks
            if action_data.animation_blocks:
                animation_block = action_data.animation_blocks[0]
                self.frames_data = animation_block.frames
                print(f"✅ Loaded {len(self.frames_data)} frames for stay animation")
                return True
            else:
                # Try to use default animation if available
                if action_data.default_animation:
                    self.frames_data = action_data.default_animation.frames
                    print(f"✅ Loaded {len(self.frames_data)} frames from default animation")
                    return True
                else:
                    print(f"⚠️  No animation blocks found for action {action_name}")
                    return False
                
        except Exception as e:
            print(f"❌ Error loading animation data: {e}")
            return False
    
    def _play_frame_sound(self):
        """Play sound for current frame if available."""
        if not self.sound_enabled or not self.frames_data:
            return
        
        try:
            current_frame_data = self.frames_data[self.current_frame_index]
            sound_path = current_frame_data.sound
            
            if sound_path and sound_path != self.last_played_sound:
                # Load and play sound via manager's sprite loader
                sound = self.manager.sprite_loader.load_sound(sound_path, self.sprite_pack_path)
                if sound:
                    # Apply volume
                    if current_frame_data.volume is not None:
                        volume_db = max(-100, min(0, current_frame_data.volume))
                        volume_linear = 10 ** (volume_db / 20.0)
                        sound.set_volume(volume_linear)
                    else:
                        sound.set_volume(self.sound_volume)
                    
                    sound.play()
                    self.last_played_sound = sound_path
                    self.sound_play_count += 1
                    
        except Exception as e:
            print(f"⚠️  Error playing sound: {e}")
    
    def get_current_frame_data(self):
        """Get current frame data."""
        if not self.frames_data or self.current_frame_index >= len(self.frames_data):
            return None
        return self.frames_data[self.current_frame_index]
    
    def get_current_sprite(self):
        """Get current frame sprite."""
        frame_data = self.get_current_frame_data()
        if not frame_data:
            return None
        
        try:
            # Load sprite via manager's sprite loader
            sprite = self.manager.sprite_loader.load_sprite(
                frame_data.image, 
                self.sprite_pack_path
            )
            if sprite:
                self.sprite_load_count += 1
            return sprite
            
        except Exception as e:
            print(f"⚠️  Error loading sprite: {e}")
            return None
    
    def set_sound_enabled(self, enabled: bool):
        """Enable or disable sound for this animation."""
        self.sound_enabled = enabled
    
    def set_sound_volume(self, volume: float):
        """Set sound volume (0.0 to 1.0)."""
        self.sound_volume = max(0.0, min(1.0, volume))
    
    def set_frame_duration(self, duration: float):
        """Set frame duration in seconds."""
        self.frame_duration = max(0.001, duration)
    
    def set_looping(self, loop: bool):
        """Set whether animation should loop."""
        self.is_looping = loop
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'total_runtime': self.total_runtime,
            'frame_count': self.frame_count,
            'sprite_load_count': self.sprite_load_count,
            'sound_play_count': self.sound_play_count,
            'current_frame': self.current_frame_index,
            'total_frames': len(self.frames_data)
        } 