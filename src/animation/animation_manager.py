# Animation Manager for Desktop Pet Application
# This module will be the MAESTRO - Central animation controller

import pygame
from pathlib import Path
from typing import Optional, Dict, Any
from utils.log_manager import get_logger

class AnimationManager:
    """MAESTRO - Central animation controller for sprite animations"""
    
    def __init__(self, sprite_name: str = "Hornet"):
        self.logger = get_logger("animation_manager")
        self.sprite_name = sprite_name
        self.current_action = "Stand"  # Default action
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 0.1  # 100ms per frame for static sprite
        
        # Sprite data from JSONParser
        self.actions = {}
        self.behaviors = {}
        self.sprite_path = None
        self.current_image = None
        
        self.logger.info(f"AnimationManager initialized for sprite: {sprite_name}")
    
    def load_sprite_data(self, json_parser):
        """Load sprite data from JSONParser"""
        try:
            # Get sprite data
            self.actions = json_parser.get_actions(self.sprite_name)
            self.behaviors = json_parser.get_behaviors(self.sprite_name)
            
            # Set sprite path
            self.sprite_path = Path("assets") / self.sprite_name
            
            self.logger.info(f"Loaded {len(self.actions)} actions and {len(self.behaviors)} behaviors for {self.sprite_name}")
            
            # Load default image (first frame of Stand action)
            if "Stand" in self.actions:
                self.set_action("Stand")
            elif self.actions:
                # Use first available action
                first_action = list(self.actions.keys())[0]
                self.set_action(first_action)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load sprite data: {e}")
            return False
    
    def set_action(self, action_name: str):
        """Set current action (for static sprite, just load the first frame)"""
        if action_name not in self.actions:
            self.logger.warning(f"Action '{action_name}' not found in {self.sprite_name}")
            return False
        
        self.current_action = action_name
        self.current_frame = 0
        self.animation_timer = 0
        
        # For static sprite, load the first image of the action
        action_data = self.actions[action_name]
        if action_data.animation_blocks:
            # Get first animation block
            anim_block = action_data.animation_blocks[0]
            if anim_block.frames:
                # Get first frame
                frame = anim_block.frames[0]
                self._load_frame_image(frame.image)
                self.logger.debug(f"Set action '{action_name}' with frame '{frame.image}'")
                return True
        
        self.logger.warning(f"No frames found for action '{action_name}'")
        return False
    
    def _load_frame_image(self, image_name: str):
        """Load frame image from sprite pack"""
        try:
            image_path = self.sprite_path / image_name
            if image_path.exists():
                self.current_image = pygame.image.load(str(image_path))
                self.logger.debug(f"Loaded image: {image_name}")
            else:
                self.logger.error(f"Image not found: {image_path}")
                # Create fallback image
                self.current_image = pygame.Surface((64, 64))
                self.current_image.fill((255, 100, 100))  # Light red
        except Exception as e:
            self.logger.error(f"Failed to load image '{image_name}': {e}")
            # Create fallback image
            self.current_image = pygame.Surface((64, 64))
            self.current_image.fill((255, 100, 100))  # Light red
    
    def update_animation(self, delta_time: float):
        """Update animation (for static sprite, do nothing)"""
        # For static sprite, no animation update needed
        pass
    
    def get_current_image(self) -> Optional[pygame.Surface]:
        """Get current frame image"""
        return self.current_image
    
    def get_current_action(self) -> str:
        """Get current action name"""
        return self.current_action
    
    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return list(self.actions.keys())
    
    def get_available_behaviors(self) -> list:
        """Get list of available behaviors"""
        return list(self.behaviors.keys()) 