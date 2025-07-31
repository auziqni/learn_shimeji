import pygame
import os
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


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
    """
    
    def __init__(self, sprite_pack_path: str, animation_name: str, frames_data: List[Dict]):
        """
        Initialize animation with sprite pack path and frame data
        
        Args:
            sprite_pack_path: Path to sprite pack folder (e.g., "assets/Hornet")
            animation_name: Name of animation (e.g., "Walk", "Sit")
            frames_data: List of frame dictionaries from XML parser
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
            # Extract frame information
            image_path = frame_data.get('Image', '')
            image_anchor = self._parse_anchor(frame_data.get('ImageAnchor', '64,128'))
            velocity = self._parse_velocity(frame_data.get('Velocity', '0,0'))
            duration = int(frame_data.get('Duration', 1))
            hotspot = frame_data.get('Hotspot')
            sound = frame_data.get('Sound')
            volume = frame_data.get('Volume')
            
            # Load sprite with caching
            sprite = self._load_sprite(image_path)
            if sprite:
                frame = AnimationFrame(
                    image=sprite,
                    image_anchor=image_anchor,
                    velocity=velocity,
                    duration=duration,
                    hotspot=hotspot,
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
    
    def _parse_anchor(self, anchor_str: str) -> Tuple[int, int]:
        """Parse anchor string like '64,128' to tuple"""
        try:
            x, y = map(int, anchor_str.split(','))
            return (x, y)
        except ValueError:
            return (64, 128)  # Default anchor
    
    def _parse_velocity(self, velocity_str: str) -> Tuple[float, float]:
        """Parse velocity string like '0,0' to tuple"""
        try:
            dx, dy = map(float, velocity_str.split(','))
            return (dx, dy)
        except ValueError:
            return (0.0, 0.0)  # Default velocity
    
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
        """Set whether animation should loop"""
        self.is_looping = loop
    
    def update(self, delta_time: float = 1.0/30.0):
        """
        Update animation state
        Called every frame (30 FPS target)
        
        Args:
            delta_time: Time since last update in seconds
        """
        if not self.is_playing or not self.frames:
            return
        
        current_frame = self.frames[self.current_frame_index]
        
        # Play sound for current frame if just started
        if self.frame_timer == 0 and current_frame.sound:
            self._play_frame_sound(current_frame)
        
        # Update frame timer
        self.frame_timer += delta_time * 30.0  # Convert to frame units
        
        # Check if it's time to advance to next frame
        if self.frame_timer >= current_frame.duration:
            self.frame_timer = 0
            self.current_frame_index += 1
            
            # Handle end of animation
            if self.current_frame_index >= len(self.frames):
                if self.is_looping:
                    self.current_frame_index = 0
                else:
                    self.is_playing = False
                    self.current_frame_index = len(self.frames) - 1
    
    def get_current_frame(self) -> Optional[AnimationFrame]:
        """Get current frame data"""
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
        return not self.is_playing and self.current_frame_index >= len(self.frames) - 1 and len(self.frames) > 0
    
    def get_frame_count(self) -> int:
        """Get total number of frames in animation"""
        return len(self.frames)
    
    def get_current_frame_index(self) -> int:
        """Get current frame index"""
        return self.current_frame_index
    
    def set_frame_index(self, index: int):
        """Set current frame index (for manual control)"""
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
        """Get sound file path for current frame"""
        current_frame = self.get_current_frame()
        if current_frame:
            return current_frame.sound
        return None
    
    def cleanup(self):
        """Clean up resources (called when animation is no longer needed)"""
        # Note: We don't clear the sprite cache here as it's shared
        # The cache will be cleared when all animations are destroyed
        self.frames.clear()
        self.is_playing = False


def clear_global_sprite_cache():
    """Clear global sprite cache to free memory"""
    global _SPRITE_CACHE
    _SPRITE_CACHE.clear()


def get_global_sprite_cache_size() -> int:
    """Get number of cached sprites"""
    return len(_SPRITE_CACHE)


def clear_global_sound_cache():
    """Clear global sound cache to free memory"""
    global _SOUND_CACHE
    _SOUND_CACHE.clear()


def get_global_sound_cache_size() -> int:
    """Get number of cached sounds"""
    return len(_SOUND_CACHE) 