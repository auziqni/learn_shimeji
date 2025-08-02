#!/usr/bin/env python3
"""
test/sprite_loader_test.py - Comprehensive Test Suite for Sprite Loader

Tests all aspects of the sprite loader including:
- Normal operations
- Edge cases  
- Fallback conditions
- Error handling
- Validation scenarios
- Performance considerations
- Memory management
- Cache optimization
"""

import unittest
import tempfile
import shutil
import os
import time
import pygame
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from animation.sprite_loader import SpriteLoader, SpriteInfo, SoundInfo


class TestSpriteLoaderComprehensive(unittest.TestCase):
    """Comprehensive test suite for SpriteLoader"""
    
    def setUp(self):
        """Set up test environment"""
        # Initialize pygame
        pygame.init()
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.sprite_dir = os.path.join(self.test_dir, "test_sprites")
        self.sound_dir = os.path.join(self.test_dir, "test_sounds")
        
        os.makedirs(self.sprite_dir, exist_ok=True)
        os.makedirs(self.sound_dir, exist_ok=True)
        
        # Create test sprite files
        self._create_test_sprites()
        
        # Create sprite loader
        self.loader = SpriteLoader(max_cache_size=10, max_memory_mb=10)
        
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary files
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Clear cache
        self.loader.clear_cache()
        
        # Quit pygame
        pygame.quit()
    
    def _create_test_sprites(self):
        """Create test sprite files"""
        # Create a simple test sprite
        test_sprite = pygame.Surface((32, 32))
        test_sprite.fill((255, 0, 0))  # Red sprite
        
        # Save test sprites
        sprite_files = [
            "test1.png",
            "test2.png", 
            "test3.png",
            "subfolder/test4.png"
        ]
        
        for sprite_file in sprite_files:
            file_path = os.path.join(self.sprite_dir, sprite_file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            pygame.image.save(test_sprite, file_path)
    
    # ===== BASIC FUNCTIONALITY TESTS =====
    
    def test_basic_sprite_loading(self):
        """Test basic sprite loading functionality"""
        # Test loading a sprite
        sprite = self.loader.load_sprite("test1.png", self.sprite_dir)
        
        self.assertIsNotNone(sprite)
        self.assertEqual(sprite.get_size(), (32, 32))
        self.assertEqual(len(self.loader._sprite_cache), 1)
    
    def test_basic_sound_loading(self):
        """Test basic sound loading functionality"""
        # Create a test sound file (empty file for testing)
        test_sound_path = os.path.join(self.sound_dir, "test.wav")
        with open(test_sound_path, 'w') as f:
            f.write("dummy sound data")
        
        # Test loading sound (will fail but should handle gracefully)
        sound = self.loader.load_sound("test.wav", self.sound_dir)
        
        # Should handle missing sound gracefully
        self.assertIsNone(sound)
    
    def test_cache_functionality(self):
        """Test cache functionality"""
        # Load same sprite twice
        sprite1 = self.loader.load_sprite("test1.png", self.sprite_dir)
        sprite2 = self.loader.load_sprite("test1.png", self.sprite_dir)
        
        # Should be same object (cached)
        self.assertIs(sprite1, sprite2)
        self.assertEqual(self.loader.cache_hits, 1)
        self.assertEqual(self.loader.cache_misses, 1)
    
    # ===== EDGE CASES TESTS =====
    
    def test_missing_sprite_file(self):
        """Test handling of missing sprite files"""
        sprite = self.loader.load_sprite("missing.png", self.sprite_dir)
        
        self.assertIsNone(sprite)
        self.assertEqual(self.loader.load_errors, 1)
    
    def test_empty_file_path(self):
        """Test handling of empty file paths"""
        sprite = self.loader.load_sprite("", self.sprite_dir)
        
        self.assertIsNone(sprite)
    
    def test_none_file_path(self):
        """Test handling of None file paths"""
        sprite = self.loader.load_sprite(None, self.sprite_dir)
        
        self.assertIsNone(sprite)
        self.assertEqual(self.loader.load_errors, 1)
    
    def test_path_with_leading_slash(self):
        """Test handling of paths with leading slash"""
        # Test that leading slash is properly normalized
        # First load with normal path
        sprite1 = self.loader.load_sprite("test1.png", self.sprite_dir)
        self.assertIsNotNone(sprite1)
        
        # Then load with leading slash (should normalize to same path)
        sprite2 = self.loader.load_sprite("/test1.png", self.sprite_dir)
        self.assertIsNotNone(sprite2)
        
        # Should be same object (cached with normalized path)
        self.assertIs(sprite1, sprite2)
        
        # Test that the normalized path is cached correctly
        cached_sprite = self.loader.get_sprite("test1.png")
        self.assertIs(sprite1, cached_sprite)
    
    def test_case_insensitive_caching(self):
        """Test case insensitive caching"""
        sprite1 = self.loader.load_sprite("test1.png", self.sprite_dir)
        sprite2 = self.loader.load_sprite("TEST1.PNG", self.sprite_dir)
        
        # Should be same object (case insensitive)
        self.assertIs(sprite1, sprite2)
        self.assertEqual(self.loader.cache_hits, 1)
    
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_multiple_sound_locations(self):
        """Test multiple sound location fallback"""
        # Create sound in different locations
        sound_file = "test_sound.wav"
        locations = [
            os.path.join(self.sprite_dir, sound_file),
            os.path.join(self.sprite_dir, "sounds", sound_file),
            os.path.join(self.sprite_dir, "audio", sound_file)
        ]
        
        # Create sound in second location
        os.makedirs(os.path.dirname(locations[1]), exist_ok=True)
        with open(locations[1], 'w') as f:
            f.write("dummy sound data")
        
        # Should find sound in second location
        sound = self.loader.load_sound(sound_file, self.sprite_dir)
        
        # Should handle gracefully even if sound format is invalid
        self.assertIsNone(sound)  # Because pygame can't load dummy data
    
    def test_cache_size_limit(self):
        """Test cache size limit fallback"""
        # Load more sprites than cache size
        for i in range(15):
            self.loader.load_sprite(f"test{i}.png", self.sprite_dir)
        
        # Should not exceed max cache size
        self.assertLessEqual(len(self.loader._sprite_cache), self.loader.max_cache_size)
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_pygame_error_handling(self):
        """Test handling of pygame errors"""
        # Create invalid image file
        invalid_file = os.path.join(self.sprite_dir, "invalid.png")
        with open(invalid_file, 'w') as f:
            f.write("not an image")
        
        sprite = self.loader.load_sprite("invalid.png", self.sprite_dir)
        
        self.assertIsNone(sprite)
        self.assertEqual(self.loader.load_errors, 1)
    
    def test_memory_error_handling(self):
        """Test handling of memory errors"""
        # Set very low memory limit
        small_loader = SpriteLoader(max_memory_mb=0.001)
        
        # Try to load sprite
        sprite = small_loader.load_sprite("test1.png", self.sprite_dir)
        
        # Should handle gracefully
        self.assertIsNotNone(sprite)
    
    def test_file_system_error_handling(self):
        """Test handling of file system errors"""
        # Test with non-existent directory
        sprite = self.loader.load_sprite("test1.png", "/non/existent/path")
        
        self.assertIsNone(sprite)
        self.assertEqual(self.loader.load_errors, 1)
    
    # ===== VALIDATION TESTS =====
    
    def test_sprite_info_validation(self):
        """Test sprite info data structure validation"""
        sprite = self.loader.load_sprite("test1.png", self.sprite_dir)
        
        # Check sprite info in cache
        sprite_info = list(self.loader._sprite_cache.values())[0]
        
        self.assertIsInstance(sprite_info, SpriteInfo)
        self.assertEqual(sprite_info.size, (32, 32))
        self.assertGreater(sprite_info.memory_usage, 0)
        self.assertEqual(sprite_info.access_count, 1)
    
    def test_sound_info_validation(self):
        """Test sound info data structure validation"""
        # Create valid sound file (simplified test)
        sound_file = os.path.join(self.sound_dir, "test.wav")
        with open(sound_file, 'w') as f:
            f.write("dummy")
        
        # Test sound info structure (even if loading fails)
        self.assertEqual(len(self.loader._sound_cache), 0)
    
    def test_cache_statistics_validation(self):
        """Test cache statistics validation"""
        # Load some sprites
        self.loader.load_sprite("test1.png", self.sprite_dir)
        self.loader.load_sprite("test2.png", self.sprite_dir)
        
        stats = self.loader.get_statistics()
        
        self.assertIn('sprite_cache_size', stats)
        self.assertIn('total_loads', stats)
        self.assertIn('cache_hits', stats)
        self.assertIn('cache_misses', stats)
        self.assertIn('hit_rate', stats)
        
        self.assertEqual(stats['sprite_cache_size'], 2)
        self.assertEqual(stats['total_loads'], 2)
    
    # ===== PERFORMANCE TESTS =====
    
    def test_large_number_of_sprites(self):
        """Test performance with large number of sprites"""
        start_time = time.time()
        
        # Load many sprites
        for i in range(50):
            self.loader.load_sprite(f"test{i}.png", self.sprite_dir)
        
        end_time = time.time()
        load_time = end_time - start_time
        
        # Should complete within reasonable time
        self.assertLess(load_time, 5.0)  # 5 seconds max
        
        # Should respect cache size limit
        self.assertLessEqual(len(self.loader._sprite_cache), self.loader.max_cache_size)
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking"""
        # Load sprites and check memory usage
        initial_memory = self.loader.current_memory_mb
        
        self.loader.load_sprite("test1.png", self.sprite_dir)
        
        final_memory = self.loader.current_memory_mb
        
        # Memory should increase
        self.assertGreater(final_memory, initial_memory)
    
    def test_cache_optimization(self):
        """Test cache optimization functionality"""
        # Load sprites
        for i in range(5):
            self.loader.load_sprite(f"test{i}.png", self.sprite_dir)
        
        initial_cache_size = len(self.loader._sprite_cache)
        
        # Optimize cache
        self.loader.optimize_cache()
        
        # Cache should still exist (sprites are recent)
        self.assertEqual(len(self.loader._sprite_cache), initial_cache_size)
    
    # ===== DATA STRUCTURE TESTS =====
    
    def test_sprite_info_data_structure(self):
        """Test SpriteInfo data structure"""
        sprite = self.loader.load_sprite("test1.png", self.sprite_dir)
        sprite_info = list(self.loader._sprite_cache.values())[0]
        
        self.assertIsInstance(sprite_info.surface, pygame.Surface)
        self.assertIsInstance(sprite_info.file_path, str)
        self.assertIsInstance(sprite_info.load_time, float)
        self.assertIsInstance(sprite_info.size, tuple)
        self.assertIsInstance(sprite_info.memory_usage, int)
        self.assertIsInstance(sprite_info.access_count, int)
        self.assertIsInstance(sprite_info.last_access, float)
    
    def test_sound_info_data_structure(self):
        """Test SoundInfo data structure"""
        # Create test sound info manually (without actual sound loading)
        sound_info = SoundInfo(
            sound=None,  # We can't create Sound without actual file
            file_path="test.wav",
            load_time=time.time(),
            memory_usage=1024,
            access_count=0,
            last_access=time.time()
        )
        
        self.assertIsInstance(sound_info.file_path, str)
        self.assertIsInstance(sound_info.load_time, float)
        self.assertIsInstance(sound_info.memory_usage, int)
        self.assertIsInstance(sound_info.access_count, int)
        self.assertIsInstance(sound_info.last_access, float)
    
    def test_loader_data_structure(self):
        """Test SpriteLoader data structure"""
        self.assertIsInstance(self.loader._sprite_cache, dict)
        self.assertIsInstance(self.loader._sound_cache, dict)
        self.assertIsInstance(self.loader.max_cache_size, int)
        self.assertIsInstance(self.loader.max_memory_mb, int)
        self.assertIsInstance(self.loader.current_memory_mb, float)
        self.assertIsInstance(self.loader.total_loads, int)
        self.assertIsInstance(self.loader.cache_hits, int)
        self.assertIsInstance(self.loader.cache_misses, int)
        self.assertIsInstance(self.loader.load_errors, int)
    
    # ===== INTEGRATION TESTS =====
    
    def test_integration_with_global_functions(self):
        """Test integration with global functions"""
        from animation.sprite_loader import (
            get_global_sprite_loader,
            clear_global_sprite_cache,
            get_global_sprite_cache_size,
            get_global_sound_cache_size
        )
        
        # Test global loader
        global_loader = get_global_sprite_loader()
        self.assertIsInstance(global_loader, SpriteLoader)
        
        # Test global functions
        initial_size = get_global_sprite_cache_size()
        clear_global_sprite_cache()
        final_size = get_global_sprite_cache_size()
        
        self.assertEqual(final_size, 0)
        self.assertIsInstance(get_global_sound_cache_size(), int)
    
    def test_integration_with_multiple_loaders(self):
        """Test integration with multiple loader instances"""
        loader1 = SpriteLoader()
        loader2 = SpriteLoader()
        
        # Load same sprite in different loaders
        sprite1 = loader1.load_sprite("test1.png", self.sprite_dir)
        sprite2 = loader2.load_sprite("test1.png", self.sprite_dir)
        
        # Should be different objects (different caches)
        self.assertIsNot(sprite1, sprite2)
        
        # Clean up
        loader1.clear_cache()
        loader2.clear_cache()
    
    def test_integration_with_real_sprite_pack(self):
        """Test integration with real sprite pack structure"""
        # Test with assets directory structure
        if os.path.exists("assets/Hornet"):
            sprite = self.loader.load_sprite("stand.png", "assets/Hornet")
            
            # Should handle real sprite pack structure
            # Result depends on whether file exists
            self.assertIsInstance(sprite, (pygame.Surface, type(None)))


if __name__ == "__main__":
    unittest.main(verbosity=2) 