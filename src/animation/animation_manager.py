# Animation Manager for Desktop Pet Application
# This module will be the MAESTRO - Central animation controller

import pygame
from pathlib import Path
from typing import Optional, Dict, Any, List
from ..utils.log_manager import get_logger
from .sprite_loader import SpriteLoader

class AnimationManager:
    """MAESTRO - Central animation controller for sprite animations"""
    
    def __init__(self, sprite_name: str = "Hornet", action_type: str = "Stay", sprite_loader: SpriteLoader = None):
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
        self.frame_anchors = []  # Store anchor points for each frame
        self.is_animating = False
        
        # Action navigation
        self.action_list = []
        self.current_action_index = 0
        
        # Sound management
        self.sounds = {}
        self.current_sound = None
        self.sound_enabled = True
        self.volume = 0.5  # Default volume (0.0 to 1.0)
        
        # Sprite loader integration
        self.sprite_loader = sprite_loader or SpriteLoader()
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.logger.info("Pygame mixer initialized for sound support")
            except Exception as e:
                self.logger.warning(f"Failed to initialize pygame mixer: {e}")
                self.sound_enabled = False
        
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
            
            # Preload sprites for this action type
            self.sprite_loader.preload_sprites(self.sprite_name, self.action_type, json_parser)
            
            # Load sounds for this sprite pack
            self._load_sounds()
            
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
    
    def _load_sounds(self):
        """Load sound files for the current sprite pack"""
        if not self.sound_enabled:
            return
        
        try:
            sounds_path = self.sprite_path / "sounds"
            if not sounds_path.exists():
                self.logger.debug(f"No sounds directory found for {self.sprite_name}")
                return
            
            # Load all sound files
            for sound_file in sounds_path.glob("*.wav"):
                sound_name = sound_file.stem
                try:
                    sound = pygame.mixer.Sound(str(sound_file))
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    self.logger.debug(f"Loaded sound: {sound_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load sound {sound_name}: {e}")
            
            for sound_file in sounds_path.glob("*.ogg"):
                sound_name = sound_file.stem
                try:
                    sound = pygame.mixer.Sound(str(sound_file))
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    self.logger.debug(f"Loaded sound: {sound_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load sound {sound_name}: {e}")
            
            self.logger.info(f"Loaded {len(self.sounds)} sounds for {self.sprite_name}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load sounds: {e}")
    
    def play_sound(self, sound_name: str):
        """Play a sound by name"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return False
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
            self.logger.debug(f"Playing sound: {sound_name}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to play sound {sound_name}: {e}")
            return False
    
    def set_volume(self, volume: float):
        """Set volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
        
        self.logger.debug(f"Volume set to: {self.volume}")
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        status = "enabled" if self.sound_enabled else "disabled"
        self.logger.info(f"Sound {status}")
        return self.sound_enabled
    
    def get_sound_status(self) -> bool:
        """Get current sound status"""
        return self.sound_enabled
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume
    
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
    
    def _play_frame_sound(self, frame_index: int):
        """Play sound for specific frame"""
        if not self.sound_enabled or frame_index >= len(self.frame_sounds):
            return
        
        frame_sound = self.frame_sounds[frame_index]
        if frame_sound and frame_sound in self.sounds:
            self.play_sound(frame_sound)
            self.logger.debug(f"Playing frame sound: {frame_sound} at frame {frame_index}")
    
    def _load_action_frames(self, action_name: str):
        """Load all frames for an action"""
        self.current_frames = []
        self.frame_durations = []
        self.frame_anchors = []  # Store anchor points for each frame
        self.frame_sounds = []  # Store sound for each frame
        
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
                
                # Store frame anchor point
                anchor = getattr(frame, 'image_anchor', None)
                self.frame_anchors.append(anchor)
                
                # Load frame sound if available (from JSON data)
                frame_sound = getattr(frame, 'sound', None)
                if frame_sound:
                    # Remove leading slash if present
                    frame_sound = frame_sound.lstrip('/')
                    # Remove .wav extension for sound name
                    frame_sound = frame_sound.replace('.wav', '').replace('.ogg', '')
                self.frame_sounds.append(frame_sound)
        
        if self.current_frames:
            self.current_image = self.current_frames[0]
            self.is_animating = len(self.current_frames) > 1
            
            # Play first frame sound if available
            if self.frame_sounds and self.frame_sounds[0]:
                self._play_frame_sound(0)
        else:
            self.logger.warning(f"No frames loaded for action '{action_name}'")
    
    def _load_frame_image(self, image_name: str) -> Optional[pygame.Surface]:
        """Load frame image using SpriteLoader"""
        if not self.sprite_path:
            self.logger.error("Sprite path not set")
            return None
        
        # Remove leading slash from image name
        clean_image_name = image_name.lstrip('/')
        
        # Construct full path to image
        image_path = self.sprite_path / clean_image_name
        
        # Use SpriteLoader to load the image
        sprite = self.sprite_loader.load_sprite(str(image_path))
        
        if sprite is None:
            self.logger.warning(f"Failed to load frame image: {image_path}")
            return None
        
        return sprite
    
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
        """Get current action info in format '[id.actiontype] : [id.actionname]'"""
        action_type = self.get_current_action_type()
        action_name = self.get_current_action()
        
        # Get action type index (1-based)
        action_type_index = self._get_action_type_index(action_type)
        
        # Get action name index (1-based)
        action_name_index = self._get_action_name_index(action_name)
        
        return f"[{action_type_index}.{action_type}] : [{action_name_index}.{action_name}]"
    
    def _get_action_type_index(self, action_type: str) -> int:
        """Get 1-based index for action type"""
        action_types = ["Stay", "Move", "Animate", "Behavior", "Embedded"]
        try:
            return action_types.index(action_type) + 1
        except ValueError:
            return 1  # Default to 1 if not found
    
    def _get_action_name_index(self, action_name: str) -> int:
        """Get 1-based index for action name within current action list"""
        try:
            return list(self.actions.keys()).index(action_name) + 1
        except ValueError:
            return 1  # Default to 1 if not found
    
    def update_animation(self, delta_time: float):
        """Update animation with proper timing and sound"""
        if not self.is_animating or not self.current_frames:
            return
        
        self.animation_timer += delta_time
        
        # Check if it's time for next frame
        if self.animation_timer >= self.frame_durations[self.current_frame]:
            self.animation_timer = 0
            old_frame = self.current_frame
            self.current_frame = (self.current_frame + 1) % len(self.current_frames)
            self.current_image = self.current_frames[self.current_frame]
            
            # Play sound for new frame if available
            self._play_frame_sound(self.current_frame)
    
    def get_current_image(self) -> Optional[pygame.Surface]:
        """Get current frame image"""
        return self.current_image
    
    def get_current_anchor(self) -> Optional[tuple]:
        """Get current frame's anchor point"""
        if self.frame_anchors and self.current_frame < len(self.frame_anchors):
            return self.frame_anchors[self.current_frame]
        return None
    
    def get_current_action(self) -> str:
        """Get current action name"""
        return self.current_action
    
    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return self.action_list
    
    def get_available_behaviors(self) -> list:
        """Get list of available behaviors"""
        return list(self.behaviors.keys())
    
    def get_sprite_loader_stats(self) -> Dict[str, Any]:
        """Get sprite loader statistics"""
        return self.sprite_loader.get_cache_stats()
    
    def get_memory_usage(self) -> tuple:
        """Get current memory usage"""
        return self.sprite_loader.get_memory_usage()
    
    def optimize_sprite_cache(self):
        """Optimize sprite cache"""
        self.sprite_loader.optimize_cache() 