import pygame
import os
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from src.utils.json_parser import JSONParser, ActionData, FrameData, AnimationBlock


@dataclass
class AnimationFrame:
    """Single frame data structure for animation"""
    image: pygame.Surface
    image_anchor: Tuple[int, int]  # (x, y) anchor point
    velocity: Tuple[float, float]  # (dx, dy) movement per frame
    duration: int  # frames to display this pose
    hotspot: Optional[Dict] = None  # interaction hotspot data
    sound: Optional[str] = None  # sound file path
    volume: Optional[int] = None  # sound volume (-100 to 0)


# Global sprite cache for memory efficiency across all animations
_SPRITE_CACHE: Dict[str, pygame.Surface] = {}

# Global sound cache for memory efficiency
_SOUND_CACHE: Dict[str, pygame.mixer.Sound] = {}


class Animation:
    """
    Single animation sequence management with efficient sprite caching
    Supports 25+ pets simultaneously with memory optimization
    Now integrated with JSON parser data structures
    """
    
    def __init__(self, sprite_pack_path: str, animation_name: str, frames_data: List[FrameData]):
        """
        Initialize animation with sprite pack path and frame data from JSON parser
        
        Args:
            sprite_pack_path: Path to sprite pack folder (e.g., "assets/Hornet")
            animation_name: Name of animation (e.g., "Walk", "Sit")
            frames_data: List of FrameData from JSON parser
        """
        self.sprite_pack_path = sprite_pack_path
        self.animation_name = animation_name
        self.frames_data = frames_data
        
        # Animation state
        self.frames: List[AnimationFrame] = []
        self.current_frame_index = 0
        self.frame_timer = 0
        self.is_playing = False
        self.is_looping = True
        
        # Sound state
        self.last_played_sound = None
        self.sound_enabled = True
        
        # Load all frames
        self._load_frames()
    
    def _load_frames(self):
        """Load all frames for this animation with efficient caching"""
        for frame_data in self.frames_data:
            # Extract frame information from FrameData
            image_path = frame_data.image
            velocity = frame_data.velocity
            duration = int(frame_data.duration * 30)  # Convert seconds to frames (30 FPS)
            sound = frame_data.sound
            volume = frame_data.volume
            
            # Load sprite with caching
            sprite = self._load_sprite(image_path)
            if sprite:
                frame = AnimationFrame(
                    image=sprite,
                    image_anchor=(64, 128),  # Default anchor, can be customized
                    velocity=velocity,
                    duration=duration,
                    hotspot=None,  # Can be extended later
                    sound=sound,
                    volume=volume
                )
                self.frames.append(frame)
    
    def _load_sprite(self, image_path: str) -> Optional[pygame.Surface]:
        """
        Load sprite with intelligent caching for memory efficiency
        Optimized for 25+ pets using shared sprite cache
        """
        if not image_path:
            return None
        
        # Remove leading slash if present
        if image_path.startswith('/'):
            image_path = image_path[1:]
        
        # Check if already loaded in global cache
        if image_path in _SPRITE_CACHE:
            return _SPRITE_CACHE[image_path]
        
        # Full path to sprite
        full_path = os.path.join(self.sprite_pack_path, image_path)
        
        try:
            # Load and optimize sprite
            sprite = pygame.image.load(full_path).convert_alpha()
            
            # Cache the sprite for reuse across multiple pets
            _SPRITE_CACHE[image_path] = sprite
            
            return sprite
            
        except (pygame.error, FileNotFoundError) as e:
            # Only print warning if it's not a video mode issue
            if "No video mode has been set" not in str(e):
                print(f"Warning: Could not load sprite {full_path}: {e}")
            return None
    
    def _load_sound(self, sound_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Load sound with intelligent caching for memory efficiency
        """
        if not sound_path:
            return None
        
        # Remove leading slash if present
        if sound_path.startswith('/'):
            sound_path = sound_path[1:]
        
        # Check if already loaded in global cache
        if sound_path in _SOUND_CACHE:
            return _SOUND_CACHE[sound_path]
        
        # Full path to sound
        full_path = os.path.join(self.sprite_pack_path, "sounds", sound_path)
        
        try:
            # Load sound
            sound = pygame.mixer.Sound(full_path)
            
            # Cache the sound for reuse
            _SOUND_CACHE[sound_path] = sound
            
            return sound
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load sound {full_path}: {e}")
            return None
    
    def _play_frame_sound(self, frame: AnimationFrame):
        """Play sound for current frame if available"""
        if not self.sound_enabled or not frame.sound:
            return
        
        try:
            sound = self._load_sound(frame.sound)
            if sound:
                # Apply volume if specified
                if frame.volume is not None:
                    # Convert volume from dB to pygame volume (0.0 to 1.0)
                    # Volume range: -100 to 0 dB
                    volume_db = max(-100, min(0, frame.volume))
                    volume_linear = 10 ** (volume_db / 20.0)
                    sound.set_volume(volume_linear)
                
                sound.play()
                self.last_played_sound = frame.sound
                
        except Exception as e:
            print(f"Warning: Could not play sound {frame.sound}: {e}")
    
    def play(self):
        """Start playing the animation"""
        self.is_playing = True
        self.current_frame_index = 0
        self.frame_timer = 0
    
    def pause(self):
        """Pause the animation"""
        self.is_playing = False
    
    def stop(self):
        """Stop and reset the animation"""
        self.is_playing = False
        self.current_frame_index = 0
        self.frame_timer = 0
    
    def set_looping(self, loop: bool):
        """Set whether the animation should loop"""
        self.is_looping = loop
    
    def update(self, delta_time: float = 1.0/30.0):
        """
        Update animation state
        
        Args:
            delta_time: Time since last update in seconds
        """
        if not self.is_playing or not self.frames:
            return
        
        current_frame = self.frames[self.current_frame_index]
        
        # Update frame timer
        self.frame_timer += delta_time
        
        # Check if it's time to move to next frame
        frame_duration = current_frame.duration / 30.0  # Convert frames to seconds
        
        if self.frame_timer >= frame_duration:
            self.frame_timer = 0
            
            # Play sound for current frame
            self._play_frame_sound(current_frame)
            
            # Move to next frame
            self.current_frame_index += 1
            
            # Handle looping
            if self.current_frame_index >= len(self.frames):
                if self.is_looping:
                    self.current_frame_index = 0
                else:
                    self.is_playing = False
                    self.current_frame_index = len(self.frames) - 1
    
    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Get the current animation frame"""
        if not self.frames or self.current_frame_index >= len(self.frames):
            return None
        return self.frames[self.current_frame_index]
    
    def get_current_velocity(self) -> Tuple[float, float]:
        """Get velocity of current frame"""
        current_frame = self.get_current_frame()
        if current_frame:
            return current_frame.velocity
        return (0.0, 0.0)
    
    def get_current_hotspot(self) -> Optional[Dict]:
        """Get hotspot data of current frame"""
        current_frame = self.get_current_frame()
        if current_frame:
            return current_frame.hotspot
        return None
    
    def is_finished(self) -> bool:
        """Check if animation has finished (for non-looping animations)"""
        return not self.is_playing and self.current_frame_index >= len(self.frames) - 1
    
    def get_frame_count(self) -> int:
        """Get total number of frames in animation"""
        return len(self.frames)
    
    def get_current_frame_index(self) -> int:
        """Get current frame index"""
        return self.current_frame_index
    
    def set_frame_index(self, index: int):
        """Set current frame index"""
        if 0 <= index < len(self.frames):
            self.current_frame_index = index
            self.frame_timer = 0
    
    def get_animation_name(self) -> str:
        """Get animation name"""
        return self.animation_name
    
    def set_sound_enabled(self, enabled: bool):
        """Enable or disable sound for this animation"""
        self.sound_enabled = enabled
    
    def get_sound_enabled(self) -> bool:
        """Get sound enabled state"""
        return self.sound_enabled
    
    def get_current_sound(self) -> Optional[str]:
        """Get current frame's sound file"""
        current_frame = self.get_current_frame()
        if current_frame:
            return current_frame.sound
        return None
    
    def cleanup(self):
        """Clean up animation resources"""
        self.is_playing = False
        # Note: We don't clear sprite cache here as it's shared across animations


class AnimationManager:
    """
    Central animation manager that integrates with JSON parser
    Manages multiple animations and pets simultaneously
    """
    
    def __init__(self, json_parser: JSONParser):
        """
        Initialize animation manager with JSON parser
        
        Args:
            json_parser: JSONParser instance for loading sprite data
        """
        self.json_parser = json_parser
        self.animations: Dict[str, Dict[str, Animation]] = {}  # sprite_name -> {action_name -> Animation}
        self.active_animations: Dict[str, Animation] = {}  # pet_id -> Animation
        
    def load_sprite_animations(self, sprite_name: str) -> bool:
        """
        Load all animations for a sprite pack
        
        Args:
            sprite_name: Name of the sprite pack (e.g., "Hornet")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get actions from JSON parser
            actions = self.json_parser.get_actions(sprite_name)
            if not actions:
                print(f"Warning: No actions found for sprite {sprite_name}")
                return False
            
            # Initialize animations dict for this sprite
            self.animations[sprite_name] = {}
            
            # Create animations for each action
            for action_name, action_data in actions.items():
                animation = self._create_animation_from_action(sprite_name, action_name, action_data)
                if animation:
                    self.animations[sprite_name][action_name] = animation
            
            print(f"✅ Loaded {len(self.animations[sprite_name])} animations for {sprite_name}")
            return True
            
        except Exception as e:
            print(f"Error loading animations for {sprite_name}: {e}")
            return False
    
    def _create_animation_from_action(self, sprite_name: str, action_name: str, action_data: ActionData) -> Optional[Animation]:
        """
        Create animation from action data
        
        Args:
            sprite_name: Name of the sprite pack
            action_name: Name of the action
            action_data: ActionData from JSON parser
            
        Returns:
            Animation instance or None if failed
        """
        try:
            # Get sprite pack path
            sprite_path = os.path.join("assets", sprite_name)
            
            # Use default animation block if available, otherwise use first block
            animation_block = action_data.default_animation
            if not animation_block and action_data.animation_blocks:
                animation_block = action_data.animation_blocks[0]
            
            if not animation_block:
                print(f"Warning: No animation blocks found for action {action_name}")
                return None
            
            # Create animation with frame data
            animation = Animation(sprite_path, action_name, animation_block.frames)
            return animation
            
        except Exception as e:
            print(f"Error creating animation for {action_name}: {e}")
            return None
    
    def get_animation(self, sprite_name: str, action_name: str) -> Optional[Animation]:
        """
        Get animation for specific sprite and action
        
        Args:
            sprite_name: Name of the sprite pack
            action_name: Name of the action
            
        Returns:
            Animation instance or None if not found
        """
        if sprite_name in self.animations and action_name in self.animations[sprite_name]:
            return self.animations[sprite_name][action_name]
        return None
    
    def start_animation(self, pet_id: str, sprite_name: str, action_name: str) -> bool:
        """
        Start animation for a specific pet
        
        Args:
            pet_id: Unique identifier for the pet
            sprite_name: Name of the sprite pack
            action_name: Name of the action
            
        Returns:
            True if successful, False otherwise
        """
        animation = self.get_animation(sprite_name, action_name)
        if animation:
            # Create a copy of the animation for this pet
            pet_animation = Animation(
                animation.sprite_pack_path,
                animation.animation_name,
                animation.frames_data
            )
            self.active_animations[pet_id] = pet_animation
            pet_animation.play()
            return True
        return False
    
    def update_pet_animation(self, pet_id: str, delta_time: float = 1.0/30.0):
        """
        Update animation for a specific pet
        
        Args:
            pet_id: Unique identifier for the pet
            delta_time: Time since last update
        """
        if pet_id in self.active_animations:
            self.active_animations[pet_id].update(delta_time)
    
    def get_pet_animation(self, pet_id: str) -> Optional[Animation]:
        """
        Get active animation for a pet
        
        Args:
            pet_id: Unique identifier for the pet
            
        Returns:
            Animation instance or None if not found
        """
        return self.active_animations.get(pet_id)
    
    def stop_pet_animation(self, pet_id: str):
        """
        Stop animation for a specific pet
        
        Args:
            pet_id: Unique identifier for the pet
        """
        if pet_id in self.active_animations:
            self.active_animations[pet_id].stop()
            del self.active_animations[pet_id]
    
    def get_available_actions(self, sprite_name: str) -> List[str]:
        """
        Get list of available actions for a sprite
        
        Args:
            sprite_name: Name of the sprite pack
            
        Returns:
            List of action names
        """
        if sprite_name in self.animations:
            return list(self.animations[sprite_name].keys())
        return []
    
    def cleanup(self):
        """Clean up all animations and clear caches"""
        for pet_id in list(self.active_animations.keys()):
            self.stop_pet_animation(pet_id)
        
        for sprite_animations in self.animations.values():
            for animation in sprite_animations.values():
                animation.cleanup()
        
        self.animations.clear()


# Global cache management functions
def clear_global_sprite_cache():
    """Clear global sprite cache"""
    global _SPRITE_CACHE
    _SPRITE_CACHE.clear()
    print("🧹 Global sprite cache cleared")


def get_global_sprite_cache_size() -> int:
    """Get number of cached sprites"""
    return len(_SPRITE_CACHE)


def clear_global_sound_cache():
    """Clear global sound cache"""
    global _SOUND_CACHE
    _SOUND_CACHE.clear()
    print("🔇 Global sound cache cleared")


def get_global_sound_cache_size() -> int:
    """Get number of cached sounds"""
    return len(_SOUND_CACHE) 