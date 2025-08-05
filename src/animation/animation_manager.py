# Animation Manager for Desktop Pet Application
# This module will be the MAESTRO - Central animation controller

import pygame
from pathlib import Path
from typing import Optional, Dict, Any, List
from utils.log_manager import get_logger

class AnimationManager:
    """MAESTRO - Central animation controller for sprite animations"""
    
    def __init__(self, sprite_name: str = "Hornet", action_type: str = "Stay"):
        self.logger = get_logger("animation_manager")
        self.sprite_name = sprite_name
        self.action_type = action_type  # Focus on specific action type
        self.current_action = "Stand"  # Default action
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 0.1  # 100ms per frame for static sprite
        
        # Sprite data from JSONParser
        self.actions = {}
        self.behaviors = {}
        self.sprite_path = None
        self.current_image = None
        
        # Animation state
        self.current_frames = []
        self.frame_durations = []
        self.is_animating = False
        
        # Action navigation
        self.action_list = []
        self.current_action_index = 0
        
        self.logger.info(f"AnimationManager initialized for sprite: {sprite_name}, action_type: {action_type}")
    
    def load_sprite_data(self, json_parser):
        """Load sprite data from JSONParser with action type filtering"""
        try:
            # Get sprite data filtered by action type
            self.actions = json_parser.get_actions_by_type(self.sprite_name, self.action_type)
            self.behaviors = json_parser.get_behaviors(self.sprite_name)
            
            # Set sprite path
            self.sprite_path = Path("assets") / self.sprite_name
            
            # Create action list for navigation (only actions of specified type)
            self.action_list = list(self.actions.keys())
            
            self.logger.info(f"Loaded {len(self.actions)} {self.action_type} actions and {len(self.behaviors)} behaviors for {self.sprite_name}")
            
            # Load default action (first in list)
            if self.action_list:
                self.set_action(self.action_list[0])
            else:
                self.logger.warning(f"No {self.action_type} actions found for {self.sprite_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load sprite data: {e}")
            return False
    
    def set_action(self, action_name: str):
        """Set current action and load its frames"""
        if action_name not in self.actions:
            self.logger.warning(f"Action '{action_name}' not found in {self.sprite_name} ({self.action_type} type)")
            return False
        
        self.current_action = action_name
        self.current_frame = 0
        self.animation_timer = 0
        
        # Update action index
        if action_name in self.action_list:
            self.current_action_index = self.action_list.index(action_name)
        
        # Load frames for this action
        self._load_action_frames(action_name)
        
        self.logger.debug(f"Set action '{action_name}' with {len(self.current_frames)} frames")
        return True
    
    def _load_action_frames(self, action_name: str):
        """Load all frames for an action"""
        self.current_frames = []
        self.frame_durations = []
        
        action_data = self.actions[action_name]
        if not action_data.animation_blocks:
            self.logger.warning(f"No animation blocks for action '{action_name}'")
            return
        
        # Get first animation block (for now)
        anim_block = action_data.animation_blocks[0]
        
        for frame in anim_block.frames:
            # Load frame image
            frame_image = self._load_frame_image(frame.image)
            if frame_image:
                self.current_frames.append(frame_image)
                # Use frame duration from XML, or default
                duration = getattr(frame, 'duration', 0.1)
                self.frame_durations.append(duration)
        
        if self.current_frames:
            self.current_image = self.current_frames[0]
            self.is_animating = len(self.current_frames) > 1
        else:
            self.logger.warning(f"No frames loaded for action '{action_name}'")
    
    def _load_frame_image(self, image_name: str) -> Optional[pygame.Surface]:
        """Load frame image from sprite pack"""
        try:
            image_path = self.sprite_path / image_name
            if image_path.exists():
                image = pygame.image.load(str(image_path))
                self.logger.debug(f"Loaded image: {image_name}")
                return image
            else:
                self.logger.error(f"Image not found: {image_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to load image '{image_name}': {e}")
            return None
    
    def next_action(self):
        """Go to next action in the list"""
        if not self.action_list:
            return False
        
        self.current_action_index = (self.current_action_index + 1) % len(self.action_list)
        new_action = self.action_list[self.current_action_index]
        return self.set_action(new_action)
    
    def previous_action(self):
        """Go to previous action in the list"""
        if not self.action_list:
            return False
        
        self.current_action_index = (self.current_action_index - 1) % len(self.action_list)
        new_action = self.action_list[self.current_action_index]
        return self.set_action(new_action)
    
    def get_current_action_type(self) -> str:
        """Get current action type"""
        return self.action_type
    
    def get_current_action_info(self) -> str:
        """Get current action info in format '[actiontype] : [actionname]'"""
        action_type = self.get_current_action_type()
        action_name = self.get_current_action()
        return f"{action_type} : {action_name}"
    
    def update_animation(self, delta_time: float):
        """Update animation with proper timing"""
        if not self.is_animating or not self.current_frames:
            return
        
        self.animation_timer += delta_time
        
        # Check if it's time for next frame
        if self.animation_timer >= self.frame_durations[self.current_frame]:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.current_frames)
            self.current_image = self.current_frames[self.current_frame]
    
    def get_current_image(self) -> Optional[pygame.Surface]:
        """Get current frame image"""
        return self.current_image
    
    def get_current_action(self) -> str:
        """Get current action name"""
        return self.current_action
    
    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return self.action_list
    
    def get_available_behaviors(self) -> list:
        """Get list of available behaviors"""
        return list(self.behaviors.keys()) 