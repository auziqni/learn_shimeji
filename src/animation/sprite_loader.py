#!/usr/bin/env python3
"""
src/animation/sprite_loader.py - Sprite Cache & Memory Management

Intelligent sprite loading and caching system optimized for 25+ concurrent pets.
Features:
- Global sprite cache for memory efficiency
- Automatic memory management
- Error handling for missing sprites
- Performance monitoring
- Memory leak prevention
"""

import pygame
import os
import time
import weakref
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass
from pathlib import Path
import gc


@dataclass
class SpriteInfo:
    """Information about a loaded sprite"""
    surface: pygame.Surface
    file_path: str
    load_time: float
    size: Tuple[int, int]
    memory_usage: int
    access_count: int = 0
    last_access: float = 0.0


@dataclass
class SoundInfo:
    """Information about a loaded sound"""
    sound: pygame.mixer.Sound
    file_path: str
    load_time: float
    memory_usage: int
    access_count: int = 0
    last_access: float = 0.0


class SpriteLoader:
    """
    Intelligent sprite loading and caching system.
    
    Optimized for 25+ concurrent pets with memory management.
    Features automatic cleanup, error handling, and performance monitoring.
    """
    
    def __init__(self, max_cache_size: int = 1000, max_memory_mb: int = 500):
        """
        Initialize sprite loader with memory constraints.
        
        Args:
            max_cache_size: Maximum number of sprites to cache
            max_memory_mb: Maximum memory usage in MB
        """
        # Cache storage
        self._sprite_cache: Dict[str, SpriteInfo] = {}
        self._sound_cache: Dict[str, SoundInfo] = {}
        
        # Memory management
        self.max_cache_size = max_cache_size
        self.max_memory_mb = max_memory_mb
        self.current_memory_mb = 0.0
        
        # Performance tracking
        self.total_loads = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.load_errors = 0
        
        # Statistics
        self.start_time = time.time()
        
        # Initialize pygame mixer if not already done
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            pass  # Mixer might already be initialized
    
    def load_sprite(self, file_path: str, sprite_pack_path: str = "") -> Optional[pygame.Surface]:
        """
        Load sprite with intelligent caching.
        
        Args:
            file_path: Relative path to sprite file
            sprite_pack_path: Base path for sprite pack
            
        Returns:
            pygame.Surface or None if loading failed
        """
        try:
            # Normalize file path
            normalized_path = self._normalize_path(file_path)
            
            # Check cache first
            if normalized_path in self._sprite_cache:
                self.cache_hits += 1
                sprite_info = self._sprite_cache[normalized_path]
                sprite_info.access_count += 1
                sprite_info.last_access = time.time()
                return sprite_info.surface
            
            # Cache miss - load from file
            self.cache_misses += 1
            full_path = self._build_full_path(file_path, sprite_pack_path)
            
            if not os.path.exists(full_path):
                print(f"Warning: Sprite file not found: {full_path}")
                self.load_errors += 1
                return None
            
            # Load sprite
            try:
                sprite = pygame.image.load(full_path).convert_alpha()
            except pygame.error:
                # Try without convert_alpha if display not initialized
                sprite = pygame.image.load(full_path)
            
            # Calculate memory usage
            memory_usage = self._calculate_sprite_memory(sprite)
            
            # Create sprite info
            sprite_info = SpriteInfo(
                surface=sprite,
                file_path=normalized_path,
                load_time=time.time(),
                size=sprite.get_size(),
                memory_usage=memory_usage,
                access_count=1,
                last_access=time.time()
            )
            
            # Add to cache
            self._add_to_sprite_cache(normalized_path, sprite_info)
            
            self.total_loads += 1
            return sprite
            
        except Exception as e:
            print(f"Error loading sprite {file_path}: {e}")
            self.load_errors += 1
            return None
    
    def load_sound(self, file_path: str, sprite_pack_path: str = "") -> Optional[pygame.mixer.Sound]:
        """
        Load sound with intelligent caching.
        
        Args:
            file_path: Relative path to sound file
            sprite_pack_path: Base path for sprite pack
            
        Returns:
            pygame.mixer.Sound or None if loading failed
        """
        try:
            # Normalize file path
            normalized_path = self._normalize_path(file_path)
            
            # Check cache first
            if normalized_path in self._sound_cache:
                sound_info = self._sound_cache[normalized_path]
                sound_info.access_count += 1
                sound_info.last_access = time.time()
                return sound_info.sound
            
            # Cache miss - load from file
            full_path = self._build_full_path(file_path, sprite_pack_path)
            
            # Try multiple possible sound locations
            sound_locations = [
                full_path,
                os.path.join(os.path.dirname(full_path), "sounds", os.path.basename(file_path)),
                os.path.join(os.path.dirname(full_path), "audio", os.path.basename(file_path))
            ]
            
            sound_file = None
            for location in sound_locations:
                if os.path.exists(location):
                    sound_file = location
                    break
            
            if not sound_file:
                print(f"Warning: Sound file not found: {file_path}")
                return None
            
            # Load sound
            sound = pygame.mixer.Sound(sound_file)
            
            # Calculate memory usage (approximate)
            memory_usage = self._calculate_sound_memory(sound)
            
            # Create sound info
            sound_info = SoundInfo(
                sound=sound,
                file_path=normalized_path,
                load_time=time.time(),
                memory_usage=memory_usage,
                access_count=1,
                last_access=time.time()
            )
            
            # Add to cache
            self._sound_cache[normalized_path] = sound_info
            
            return sound
            
        except Exception as e:
            print(f"Error loading sound {file_path}: {e}")
            return None
    
    def get_sprite(self, file_path: str) -> Optional[pygame.Surface]:
        """
        Get sprite from cache without loading.
        
        Args:
            file_path: Normalized file path
            
        Returns:
            pygame.Surface or None if not in cache
        """
        normalized_path = self._normalize_path(file_path)
        if normalized_path in self._sprite_cache:
            sprite_info = self._sprite_cache[normalized_path]
            sprite_info.access_count += 1
            sprite_info.last_access = time.time()
            return sprite_info.surface
        return None
    
    def get_sound(self, file_path: str) -> Optional[pygame.mixer.Sound]:
        """
        Get sound from cache without loading.
        
        Args:
            file_path: Normalized file path
            
        Returns:
            pygame.mixer.Sound or None if not in cache
        """
        normalized_path = self._normalize_path(file_path)
        if normalized_path in self._sound_cache:
            sound_info = self._sound_cache[normalized_path]
            sound_info.access_count += 1
            sound_info.last_access = time.time()
            return sound_info.sound
        return None
    
    def clear_cache(self, sprite_pack: str = None):
        """
        Clear cache for specific sprite pack or all.
        
        Args:
            sprite_pack: Specific sprite pack to clear, or None for all
        """
        if sprite_pack:
            # Clear specific sprite pack
            keys_to_remove = []
            for key in self._sprite_cache:
                if sprite_pack in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._sprite_cache[key]
            
            # Clear sounds for sprite pack
            keys_to_remove = []
            for key in self._sound_cache:
                if sprite_pack in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._sound_cache[key]
        else:
            # Clear all cache
            self._sprite_cache.clear()
            self._sound_cache.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Recalculate memory usage
        self._update_memory_usage()
    
    def optimize_cache(self):
        """
        Optimize cache by removing least used items.
        """
        current_time = time.time()
        
        # Remove sprites that haven't been accessed recently
        keys_to_remove = []
        for key, sprite_info in self._sprite_cache.items():
            if current_time - sprite_info.last_access > 300:  # 5 minutes
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._sprite_cache[key]
        
        # Remove sounds that haven't been accessed recently
        keys_to_remove = []
        for key, sound_info in self._sound_cache.items():
            if current_time - sound_info.last_access > 300:  # 5 minutes
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._sound_cache[key]
        
        # Force garbage collection
        gc.collect()
        
        # Recalculate memory usage
        self._update_memory_usage()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        self._update_memory_usage()
        
        return {
            'sprite_cache_size': len(self._sprite_cache),
            'sound_cache_size': len(self._sound_cache),
            'total_memory_mb': self.current_memory_mb,
            'max_memory_mb': self.max_memory_mb,
            'total_loads': self.total_loads,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'load_errors': self.load_errors,
            'hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            'uptime_seconds': time.time() - self.start_time
        }
    
    def print_statistics(self):
        """Print cache statistics to console."""
        stats = self.get_statistics()
        
        print(f"\n📊 Sprite Loader Statistics:")
        print(f"{'='*40}")
        print(f"Sprite Cache: {stats['sprite_cache_size']} sprites")
        print(f"Sound Cache: {stats['sound_cache_size']} sounds")
        print(f"Memory Usage: {stats['total_memory_mb']:.1f}MB / {stats['max_memory_mb']}MB")
        print(f"Total Loads: {stats['total_loads']}")
        print(f"Cache Hits: {stats['cache_hits']}")
        print(f"Cache Misses: {stats['cache_misses']}")
        print(f"Hit Rate: {stats['hit_rate']:.1%}")
        print(f"Load Errors: {stats['load_errors']}")
        print(f"Uptime: {stats['uptime_seconds']:.1f}s")
    
    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path for consistent caching."""
        if not file_path:
            return ""
        
        # Remove leading slash if present
        if file_path.startswith('/'):
            file_path = file_path[1:]
        
        # Convert to lowercase for case-insensitive caching
        return file_path.lower()
    
    def _build_full_path(self, file_path: str, sprite_pack_path: str) -> str:
        """Build full file path."""
        if not file_path:
            return ""
        
        if sprite_pack_path:
            return os.path.join(sprite_pack_path, file_path)
        return file_path
    
    def _calculate_sprite_memory(self, sprite: pygame.Surface) -> int:
        """Calculate approximate memory usage of sprite."""
        width, height = sprite.get_size()
        # Approximate: 4 bytes per pixel for RGBA
        return width * height * 4
    
    def _calculate_sound_memory(self, sound: pygame.mixer.Sound) -> int:
        """Calculate approximate memory usage of sound."""
        # This is a rough estimate - pygame doesn't expose sound size
        # Assume 1MB per sound file as approximation
        return 1024 * 1024
    
    def _add_to_sprite_cache(self, key: str, sprite_info: SpriteInfo):
        """Add sprite to cache with memory management."""
        # Check if we need to free memory
        if len(self._sprite_cache) >= self.max_cache_size:
            self._remove_least_used_sprite()
        
        # Check memory limit
        while self.current_memory_mb > self.max_memory_mb and self._sprite_cache:
            self._remove_least_used_sprite()
        
        # Add to cache
        self._sprite_cache[key] = sprite_info
        self._update_memory_usage()
    
    def _remove_least_used_sprite(self):
        """Remove least used sprite from cache."""
        if not self._sprite_cache:
            return
        
        # Find least used sprite
        least_used_key = min(
            self._sprite_cache.keys(),
            key=lambda k: (self._sprite_cache[k].access_count, self._sprite_cache[k].last_access)
        )
        
        # Remove from cache
        del self._sprite_cache[least_used_key]
    
    def _update_memory_usage(self):
        """Update current memory usage calculation."""
        sprite_memory = sum(info.memory_usage for info in self._sprite_cache.values())
        sound_memory = sum(info.memory_usage for info in self._sound_cache.values())
        
        self.current_memory_mb = float((sprite_memory + sound_memory) / (1024 * 1024))


# Global sprite loader instance
_global_sprite_loader: Optional[SpriteLoader] = None


def get_global_sprite_loader() -> SpriteLoader:
    """Get global sprite loader instance."""
    global _global_sprite_loader
    if _global_sprite_loader is None:
        _global_sprite_loader = SpriteLoader()
    return _global_sprite_loader


def clear_global_sprite_cache():
    """Clear global sprite cache."""
    loader = get_global_sprite_loader()
    loader.clear_cache()


def get_global_sprite_cache_size() -> int:
    """Get global sprite cache size."""
    loader = get_global_sprite_loader()
    return len(loader._sprite_cache)


def get_global_sound_cache_size() -> int:
    """Get global sound cache size."""
    loader = get_global_sprite_loader()
    return len(loader._sound_cache)


def clear_global_sound_cache():
    """Clear global sound cache."""
    loader = get_global_sprite_loader()
    loader.clear_cache()  # This clears both sprites and sounds


if __name__ == "__main__":
    # Simple test when run directly
    loader = SpriteLoader()
    print("✅ SpriteLoader initialized successfully")
    print(f"Cache size: {len(loader._sprite_cache)} sprites")
    print(f"Memory usage: {loader.current_memory_mb:.1f}MB") 