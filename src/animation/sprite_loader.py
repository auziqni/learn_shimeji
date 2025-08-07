# Sprite Loader for Desktop Pet Application
# This module handles sprite cache & memory management

import pygame
import os
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from collections import OrderedDict
from ..utils.log_manager import get_logger

class SpriteLoader:
    """Robust sprite cache & memory management for sprite animations"""
    
    def __init__(self, cache_size: int = 100, memory_limit_mb: int = 50, settings_manager=None):
        """Initialize sprite loader with cache and memory management"""
        self.cache = {}
        self.cache_size = cache_size
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.settings_manager = settings_manager
        self.logger = get_logger("sprite_loader")
        
        # LRU Cache for sprites
        self.sprite_cache = OrderedDict()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'loads': 0,
            'evictions': 0
        }
        
        # Memory tracking
        self.current_memory_usage = 0
        self.sprite_sizes = {}
        
        # Check if pygame display is initialized
        self.display_initialized = pygame.display.get_init()
        
        self.logger.info(f"SpriteLoader initialized with cache_size={cache_size}, memory_limit={memory_limit_mb}MB")
        self.logger.info(f"Pygame display initialized: {self.display_initialized}")
    
    def load_sprite(self, sprite_path: str) -> Optional[pygame.Surface]:
        """Load sprite with smart caching and memory management"""
        try:
            # Check if sprite is already cached
            if sprite_path in self.sprite_cache:
                # Move to end (LRU)
                sprite = self.sprite_cache.pop(sprite_path)
                self.sprite_cache[sprite_path] = sprite
                self.cache_stats['hits'] += 1
                return sprite
            
            # Cache miss - load from disk
            self.cache_stats['misses'] += 1
            sprite = self._load_from_disk(sprite_path)
            
            if sprite is not None:
                # Add to cache with memory management
                self._add_to_cache(sprite_path, sprite)
                self.cache_stats['loads'] += 1
                return sprite
            else:
                self.logger.warning(f"Failed to load sprite: {sprite_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading sprite {sprite_path}: {e}")
            return None
    
    def _load_from_disk(self, sprite_path: str) -> Optional[pygame.Surface]:
        """Load sprite from disk with error handling"""
        try:
            # Check if file exists
            if not os.path.exists(sprite_path):
                self.logger.warning(f"Sprite file not found: {sprite_path}")
                return None
            
            # Try to load the sprite
            sprite = pygame.image.load(sprite_path)

            # Convert to optimize for display - handle display not initialized
            try:
                if sprite.get_alpha() is None:
                    sprite = sprite.convert()
                else:
                    sprite = sprite.convert_alpha()
            except pygame.error as e:
                if "cannot convert without pygame.display initialized" in str(e):
                    # Create a dummy display surface for conversion
                    try:
                        dummy_surface = pygame.Surface((1, 1))
                        if sprite.get_alpha() is None:
                            sprite = sprite.convert(dummy_surface)
                        else:
                            sprite = sprite.convert_alpha(dummy_surface)
                    except:
                        # If all else fails, use as-is
                        pass
                else:
                    raise e

            # Preprocess alpha pixels to prevent bleeding
            sprite = self._preprocess_alpha_pixels(sprite)
            
            
            return sprite
            
        except pygame.error as e:
            self.logger.warning(f"Pygame error loading {sprite_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error loading {sprite_path}: {e}")
            return None
    
    def _preprocess_sprite_for_transparency(self, sprite: pygame.Surface, transparency_color=(255, 0, 255)) -> pygame.Surface:
        """Preprocess sprite to avoid color key conflicts"""
        try:
            # Create a copy to avoid modifying original
            processed_sprite = sprite.copy()
            
            # Get the surface array for pixel manipulation
            pixel_array = pygame.PixelArray(processed_sprite)
            
            # Define tolerance for color matching (to avoid bleeding)
            tolerance = 30  # Adjust this value as needed
            
            # Get transparency color components
            r_target, g_target, b_target = transparency_color
            
            # Scan and adjust pixels that are too close to transparency color
            for x in range(processed_sprite.get_width()):
                for y in range(processed_sprite.get_height()):
                    # Get pixel color
                    pixel_color = processed_sprite.get_at((x, y))
                    r, g, b, a = pixel_color
                    
                    # Skip fully transparent pixels
                    if a == 0:
                        continue
                    
                    # Calculate distance from transparency color
                    distance = ((r - r_target) ** 2 + (g - g_target) ** 2 + (b - b_target) ** 2) ** 0.5
                    
                    # If pixel is too close to transparency color, adjust it
                    if distance < tolerance:
                        # Move the color away from transparency color
                        if r < r_target:
                            r = max(0, r - 10)
                        else:
                            r = min(255, r + 10)
                        
                        if g < g_target:
                            g = max(0, g - 10)
                        else:
                            g = min(255, g + 10)
                        
                        if b < b_target:
                            b = max(0, b - 10)
                        else:
                            b = min(255, b + 10)
                        
                        # Set the adjusted pixel
                        processed_sprite.set_at((x, y), (r, g, b, a))
            
            # Clean up pixel array
            pixel_array.close()
            
            self.logger.debug(f"Sprite preprocessed to avoid transparency conflicts")
            return processed_sprite
            
        except Exception as e:
            self.logger.warning(f"Failed to preprocess sprite: {e}")
            return sprite  # Return original if preprocessing fails
    
    def _preprocess_alpha_pixels(self, sprite: pygame.Surface) -> pygame.Surface:
        """Convert RGBA to RGB to prevent bleeding with color key transparency"""
        try:
            # Check if preprocessing is enabled
            if hasattr(self, 'settings_manager') and self.settings_manager:
                if not self.settings_manager.get_preprocess_alpha():
                    return sprite  # Skip preprocessing if disabled
            
            # Create a copy to avoid modifying original
            processed_sprite = sprite.copy()
            
            # Get pixel array for manipulation
            pixel_array = pygame.PixelArray(processed_sprite)
            
            # Track conversion stats
            converted_pixels = 0
            total_pixels = sprite.get_width() * sprite.get_height()
            
            # Process each pixel
            for x in range(sprite.get_width()):
                for y in range(sprite.get_height()):
                    pixel = sprite.get_at((x, y))
                    
                    if len(pixel) == 4:  # RGBA
                        r, g, b, a = pixel
                        
                        if a == 255:
                            # Keep original color (fully opaque)
                            new_color = (r, g, b)
                            pixel_array[x, y] = new_color
                        elif a == 0:
                            # Keep transparent (fully transparent)
                            # Don't change - keep as transparent
                            pass
                        else:
                            # Convert semi-transparent to solid RGB (remove alpha)
                            new_color = (r, g, b)
                            pixel_array[x, y] = new_color
                            converted_pixels += 1
            
            # Log preprocessing results
            if converted_pixels > 0:
                conversion_percentage = (converted_pixels / total_pixels) * 100
                self.logger.info(f"RGBA to RGB conversion: {converted_pixels}/{total_pixels} pixels converted ({conversion_percentage:.1f}%)")
            else:
                self.logger.info(f"RGBA to RGB conversion: No pixels converted (sprite may not have alpha channel)")
            
            return processed_sprite
            
        except Exception as e:
            self.logger.error(f"Failed to convert RGBA to RGB: {e}")
            return sprite  # Return original if processing fails
    
    def _add_to_cache(self, sprite_path: str, sprite: pygame.Surface):
        """Add sprite to cache with memory management"""
        # Calculate sprite memory usage
        sprite_size = sprite.get_width() * sprite.get_height() * 4  # 4 bytes per pixel (RGBA)
        
        # Check if we need to evict sprites
        while (len(self.sprite_cache) >= self.cache_size or 
               self.current_memory_usage + sprite_size > self.memory_limit_bytes):
            self._evict_oldest_sprite()
        
        # Add to cache
        self.sprite_cache[sprite_path] = sprite
        self.sprite_sizes[sprite_path] = sprite_size
        self.current_memory_usage += sprite_size
        
        self.logger.debug(f"Added {sprite_path} to cache (size: {sprite_size/1024:.1f}KB)")
    
    def _evict_oldest_sprite(self):
        """Evict oldest sprite from cache (LRU)"""
        if not self.sprite_cache:
            return
        
        # Remove oldest sprite
        oldest_path, oldest_sprite = self.sprite_cache.popitem(last=False)
        oldest_size = self.sprite_sizes.pop(oldest_path, 0)
        self.current_memory_usage -= oldest_size
        self.cache_stats['evictions'] += 1
        
        self.logger.debug(f"Evicted {oldest_path} from cache")
    
    def preload_sprites(self, sprite_pack: str, action_type: str, json_parser) -> Dict[str, bool]:
        """Preload all sprites for a specific action type"""
        self.logger.info(f"Preloading sprites for {sprite_pack}/{action_type}")
        
        # Get actions for this type
        actions = json_parser.get_actions_by_type(sprite_pack, action_type)
        sprite_path = Path("assets") / sprite_pack
        
        preload_results = {}
        loaded_count = 0
        
        for action_name, action_data in actions.items():
            if not action_data.animation_blocks:
                continue
            
            # Get first animation block
            anim_block = action_data.animation_blocks[0]
            
            for frame in anim_block.frames:
                # Remove leading slash from image path
                image_name = frame.image.lstrip('/')
                image_path = sprite_path / image_name
                if image_path.exists():
                    sprite = self.load_sprite(str(image_path))
                    if sprite is not None:
                        preload_results[str(image_path)] = True
                        loaded_count += 1
                    else:
                        preload_results[str(image_path)] = False
                else:
                    preload_results[str(image_path)] = False
                    self.logger.warning(f"Sprite not found: {image_path}")
        
        self.logger.info(f"Preloaded {loaded_count} sprites for {sprite_pack}/{action_type}")
        return preload_results
    
    def get_sprite(self, sprite_path: str) -> Optional[pygame.Surface]:
        """Get sprite from cache or load if not cached (alias for load_sprite)"""
        return self.load_sprite(sprite_path)
    
    def clear_cache(self):
        """Clear entire sprite cache"""
        self.sprite_cache.clear()
        self.sprite_sizes.clear()
        self.current_memory_usage = 0
        self.cache_stats['evictions'] += len(self.sprite_cache)
        
        self.logger.info("Sprite cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        stats = self.cache_stats.copy()
        stats['cache_size'] = len(self.sprite_cache)
        stats['memory_usage_mb'] = self.current_memory_usage / (1024 * 1024)
        total_requests = stats['hits'] + stats['misses']
        stats['hit_rate'] = (stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        return stats
    
    def get_memory_usage(self) -> Tuple[int, int]:
        """Get current memory usage in bytes and percentage"""
        percentage = (self.current_memory_usage / self.memory_limit_bytes) * 100 if self.memory_limit_bytes > 0 else 0
        return self.current_memory_usage, percentage
    
    def optimize_cache(self):
        """Optimize cache by removing least used sprites"""
        if len(self.sprite_cache) > self.cache_size * 0.8:  # 80% full
            # Remove 20% of oldest sprites
            remove_count = int(len(self.sprite_cache) * 0.2)
            for _ in range(remove_count):
                self._evict_oldest_sprite()
            
            self.logger.info(f"Cache optimized: removed {remove_count} sprites")
    
    def is_cached(self, sprite_path: str) -> bool:
        """Check if sprite is cached"""
        return sprite_path in self.sprite_cache 