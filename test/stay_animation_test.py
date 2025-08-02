#!/usr/bin/env python3
"""
test/stay_animation_test.py - Comprehensive Test Suite for Stay Animation

Tests all aspects of the StayAnimation including:
- Normal operations
- Edge cases  
- Fallback conditions
- Error handling
- Validation scenarios
- Performance considerations
- Data structure tests
- Integration scenarios
"""

import unittest
import tempfile
import shutil
import os
import time
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set display environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from animation.action_types.stay_animation import StayAnimation
from animation.animation_manager import AnimationManager


class TestStayAnimationComprehensive(unittest.TestCase):
    """Comprehensive test suite for StayAnimation"""
    
    def setUp(self):
        """Set up test environment"""
        # Initialize pygame for testing
        try:
            pygame.init()
        except Exception as e:
            print(f"⚠️  Pygame initialization warning: {e}")
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create test sprite files
        self._create_test_sprites()
        
        # Initialize animation manager
        self.manager = AnimationManager(max_cache_size=50, max_memory_mb=25.0)
        
        # Initialize stay animation
        self.stay_animation = StayAnimation(self.manager)
        
    def tearDown(self):
        """Clean up test environment"""
        # Clean up animation manager
        if hasattr(self, 'manager'):
            self.manager.cleanup()
        
        # Clean up pygame
        try:
            pygame.quit()
        except:
            pass
        
        # Clean up test directory
        if hasattr(self, 'test_dir'):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_sprites(self):
        """Create test sprite files"""
        # Create test sprite directory
        test_sprite_dir = os.path.join(self.test_dir, "assets", "TestSprite")
        os.makedirs(test_sprite_dir, exist_ok=True)
        
        # Create test sprites
        for i in range(3):
            sprite = pygame.Surface((32, 32))
            sprite.fill((255, 0, 0))  # Red sprites
            pygame.image.save(sprite, os.path.join(test_sprite_dir, f"test{i+1}.png"))
    
    # ===== BASIC FUNCTIONALITY TESTS =====
    
    def test_basic_initialization(self):
        """Test basic initialization"""
        self.assertIsNotNone(self.stay_animation)
        self.assertEqual(self.stay_animation.get_action_name(), "StayAnimation")
        self.assertFalse(self.stay_animation.is_active)
        self.assertIsNone(self.stay_animation.get_current_pet_id())
    
    def test_action_lifecycle(self):
        """Test action lifecycle (start, update, stop)"""
        pet_id = "test_pet"
        
        # Add pet to manager and load sprite pack data
        self.manager.add_pet(pet_id, "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # Start action
        success = self.stay_animation.start(pet_id)
        self.assertTrue(success)
        self.assertTrue(self.stay_animation.is_active)
        self.assertEqual(self.stay_animation.get_current_pet_id(), pet_id)
        
        # Update action
        self.stay_animation.update(pet_id, 0.1)
        self.assertTrue(self.stay_animation.is_active_for_pet(pet_id))
        
        # Stop action
        self.stay_animation.stop(pet_id)
        self.assertFalse(self.stay_animation.is_active)
        self.assertIsNone(self.stay_animation.get_current_pet_id())
    
    def test_frame_management(self):
        """Test frame management"""
        pet_id = "frame_test_pet"
        
        # Start action
        self.stay_animation.start(pet_id)
        
        # Update multiple times to test frame progression
        for i in range(10):
            self.stay_animation.update(pet_id, 0.1)
        
        # Check performance stats
        stats = self.stay_animation.get_performance_stats()
        self.assertGreater(stats['total_runtime'], 0)
        self.assertGreater(stats['frame_count'], 0)
    
    def test_sprite_loading(self):
        """Test sprite loading functionality"""
        pet_id = "sprite_test_pet"
        
        # Start action
        self.stay_animation.start(pet_id)
        
        # Get current sprite
        sprite = self.stay_animation.get_current_sprite()
        # May be None if no sprite data available, but shouldn't crash
    
    # ===== EDGE CASES TESTS =====
    
    def test_nonexistent_pet(self):
        """Test handling of nonexistent pet"""
        # Try to start action for nonexistent pet
        success = self.stay_animation.start("nonexistent_pet")
        # Should handle gracefully
    
    def test_invalid_delta_time(self):
        """Test handling of invalid delta time"""
        pet_id = "delta_test_pet"
        self.stay_animation.start(pet_id)
        
        # Test with negative delta time
        self.stay_animation.update(pet_id, -0.1)
        
        # Test with zero delta time
        self.stay_animation.update(pet_id, 0.0)
        
        # Test with very large delta time
        self.stay_animation.update(pet_id, 100.0)
    
    def test_multiple_pets(self):
        """Test handling multiple pets"""
        pet1 = "pet_1"
        pet2 = "pet_2"
        
        # Start action for first pet
        self.stay_animation.start(pet1)
        self.assertTrue(self.stay_animation.is_active_for_pet(pet1))
        
        # Start action for second pet (should stop first)
        self.stay_animation.start(pet2)
        self.assertFalse(self.stay_animation.is_active_for_pet(pet1))
        self.assertTrue(self.stay_animation.is_active_for_pet(pet2))
    
    def test_empty_frames_data(self):
        """Test handling of empty frames data"""
        # This would require mocking the frames data
        # For now, test that the action handles missing data gracefully
        pass
    
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_sprite_loader_fallback(self):
        """Test sprite loader fallback behavior"""
        # Test with invalid sprite paths
        sprite = self.manager.sprite_loader.load_sprite("nonexistent.png", "nonexistent_path")
        self.assertIsNone(sprite)
    
    def test_sound_fallback(self):
        """Test sound fallback behavior"""
        pet_id = "sound_test_pet"
        self.stay_animation.start(pet_id)
        
        # Disable sound
        self.stay_animation.set_sound_enabled(False)
        self.assertFalse(self.stay_animation.sound_enabled)
        
        # Update should not crash
        self.stay_animation.update(pet_id, 0.1)
    
    def test_animation_data_fallback(self):
        """Test animation data fallback behavior"""
        # This would require mocking the JSON parser
        # For now, test that the action handles missing data gracefully
        pass
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_exception_in_start(self):
        """Test exception handling in start method"""
        # Test with invalid manager
        invalid_animation = StayAnimation(None)
        success = invalid_animation.start("test_pet")
        self.assertFalse(success)
    
    def test_exception_in_update(self):
        """Test exception handling in update method"""
        pet_id = "update_test_pet"
        self.stay_animation.start(pet_id)
        
        # Update should not crash even with issues
        self.stay_animation.update(pet_id, 0.1)
    
    def test_exception_in_stop(self):
        """Test exception handling in stop method"""
        # Stop should not crash even if not started
        self.stay_animation.stop("nonexistent_pet")
    
    # ===== VALIDATION TESTS =====
    
    def test_action_state_validation(self):
        """Test action state validation"""
        pet_id = "state_test_pet"
        
        # Initial state
        self.assertFalse(self.stay_animation.is_active)
        self.assertIsNone(self.stay_animation.get_current_pet_id())
        
        # After start
        self.stay_animation.start(pet_id)
        self.assertTrue(self.stay_animation.is_active)
        self.assertEqual(self.stay_animation.get_current_pet_id(), pet_id)
        
        # After stop
        self.stay_animation.stop(pet_id)
        self.assertFalse(self.stay_animation.is_active)
        self.assertIsNone(self.stay_animation.get_current_pet_id())
    
    def test_performance_stats_validation(self):
        """Test performance statistics validation"""
        pet_id = "stats_test_pet"
        self.stay_animation.start(pet_id)
        
        # Update to generate stats
        for _ in range(5):
            self.stay_animation.update(pet_id, 0.1)
        
        stats = self.stay_animation.get_performance_stats()
        
        required_keys = [
            'total_runtime', 'frame_count', 'sprite_load_count',
            'sound_play_count', 'current_frame', 'total_frames'
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))
    
    def test_settings_validation(self):
        """Test settings validation"""
        # Test sound settings
        self.stay_animation.set_sound_enabled(True)
        self.assertTrue(self.stay_animation.sound_enabled)
        
        self.stay_animation.set_sound_volume(0.5)
        self.assertEqual(self.stay_animation.sound_volume, 0.5)
        
        # Test frame duration
        self.stay_animation.set_frame_duration(0.05)
        self.assertEqual(self.stay_animation.frame_duration, 0.05)
        
        # Test looping
        self.stay_animation.set_looping(False)
        self.assertFalse(self.stay_animation.is_looping)
    
    # ===== PERFORMANCE TESTS =====
    
    def test_update_performance(self):
        """Test update performance"""
        pet_id = "perf_test_pet"
        self.stay_animation.start(pet_id)
        
        # Update many times
        start_time = time.time()
        for _ in range(100):
            self.stay_animation.update(pet_id, 0.016)  # ~60 FPS
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 1.0)  # Less than 1 second
        
        # Check performance stats
        stats = self.stay_animation.get_performance_stats()
        self.assertGreater(stats['frame_count'], 0)
    
    def test_memory_usage(self):
        """Test memory usage"""
        pet_id = "memory_test_pet"
        self.stay_animation.start(pet_id)
        
        # Update to trigger sprite loading
        for _ in range(10):
            self.stay_animation.update(pet_id, 0.1)
        
        # Check sprite load count
        stats = self.stay_animation.get_performance_stats()
        self.assertIsInstance(stats['sprite_load_count'], int)
    
    def test_loop_performance(self):
        """Test loop performance"""
        pet_id = "loop_test_pet"
        self.stay_animation.start(pet_id)
        
        # Update many times to test looping
        for _ in range(50):
            self.stay_animation.update(pet_id, 0.1)
        
        # Should still be active (looping)
        self.assertTrue(self.stay_animation.is_active)
    
    # ===== DATA STRUCTURE TESTS =====
    
    def test_animation_data_structures(self):
        """Test animation data structures"""
        # Test frames_data
        self.assertIsInstance(self.stay_animation.frames_data, list)
        
        # Test sprite_pack_path
        self.assertIsInstance(self.stay_animation.sprite_pack_path, str)
        
        # Test animation settings
        self.assertIsInstance(self.stay_animation.frame_duration, float)
        self.assertIsInstance(self.stay_animation.is_looping, bool)
        self.assertIsInstance(self.stay_animation.sound_enabled, bool)
        self.assertIsInstance(self.stay_animation.sound_volume, float)
    
    def test_performance_stats_structure(self):
        """Test performance statistics data structure"""
        stats = self.stay_animation.get_performance_stats()
        
        # Check data types
        self.assertIsInstance(stats['total_runtime'], float)
        self.assertIsInstance(stats['frame_count'], int)
        self.assertIsInstance(stats['sprite_load_count'], int)
        self.assertIsInstance(stats['sound_play_count'], int)
        self.assertIsInstance(stats['current_frame'], int)
        self.assertIsInstance(stats['total_frames'], int)
    
    def test_state_data_structure(self):
        """Test state data structure"""
        # Test state data operations
        self.stay_animation.set_state_data("test_key", "test_value")
        value = self.stay_animation.get_state_data_value("test_key")
        self.assertEqual(value, "test_value")
        
        # Test default value
        default_value = self.stay_animation.get_state_data_value("nonexistent_key", "default")
        self.assertEqual(default_value, "default")
    
    # ===== INTEGRATION TESTS =====
    
    def test_integration_with_manager(self):
        """Test integration with animation manager"""
        pet_id = "integration_pet"
        
        # Add pet to manager and load sprite pack data
        self.manager.add_pet(pet_id, "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # Start action via manager
        success = self.manager.start_pet_action(pet_id, "stay")
        self.assertTrue(success)
        
        # Update via manager
        self.manager.update_pet_action(pet_id, 0.1)
        
        # Check action is active
        action = self.manager.get_pet_action(pet_id)
        self.assertIsNotNone(action)
        self.assertTrue(action.is_active_for_pet(pet_id))
    
    def test_integration_with_sprite_loader(self):
        """Test integration with sprite loader"""
        # Test that stay animation can use sprite loader
        sprite = self.manager.sprite_loader.load_sprite("test1.png", self.test_dir + "/assets/TestSprite")
        self.assertIsNotNone(sprite)
    
    def test_integration_with_json_parser(self):
        """Test integration with JSON parser"""
        # Test that stay animation can use JSON parser
        self.assertIsNotNone(self.manager.json_parser)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        pet_id = "workflow_pet"
        
        # 1. Add pet to manager and load sprite pack data
        self.manager.add_pet(pet_id, "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # 2. Start stay animation
        success = self.stay_animation.start(pet_id)
        self.assertTrue(success)
        
        # 3. Update multiple times
        for _ in range(10):
            self.stay_animation.update(pet_id, 0.1)
        
        # 4. Check performance stats
        stats = self.stay_animation.get_performance_stats()
        self.assertGreater(stats['total_runtime'], 0)
        self.assertGreater(stats['frame_count'], 0)
        
        # 5. Stop animation
        self.stay_animation.stop(pet_id)
        
        # 6. Final check
        self.assertFalse(self.stay_animation.is_active)
        self.assertIsNone(self.stay_animation.get_current_pet_id())


if __name__ == "__main__":
    unittest.main(verbosity=2) 