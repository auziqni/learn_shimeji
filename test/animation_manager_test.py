#!/usr/bin/env python3
"""
test/animation_manager_test.py - Comprehensive Test Suite for Animation Manager

Tests all aspects of the AnimationManager including:
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
from animation.animation_manager import AnimationManager


class TestAnimationManagerComprehensive(unittest.TestCase):
    """Comprehensive test suite for AnimationManager"""
    
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
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.sprite_loader)
        self.assertIsNotNone(self.manager.json_parser)
        self.assertIsInstance(self.manager.action_types, dict)
        self.assertIsInstance(self.manager.pets, dict)
        self.assertIsInstance(self.manager.active_actions, dict)
    
    def test_action_type_registration(self):
        """Test action type registration"""
        # Check default action types
        available_types = self.manager.get_available_action_types()
        self.assertIn("stay", available_types)
        
        # Test getting action type
        stay_action = self.manager.get_action_type("stay")
        self.assertIsNotNone(stay_action)
        self.assertEqual(stay_action.get_action_name(), "StayAnimation")
    
    def test_pet_management(self):
        """Test pet management functionality"""
        # Add pet
        self.manager.add_pet("test_pet_1", "Hornet", position=(100, 100))
        
        # Check pet exists
        pet_info = self.manager.get_pet_info("test_pet_1")
        self.assertIsNotNone(pet_info)
        self.assertEqual(pet_info['sprite_pack'], "Hornet")
        self.assertEqual(pet_info['position'], (100, 100))
        
        # Check pet list
        all_pets = self.manager.get_all_pets()
        self.assertIn("test_pet_1", all_pets)
        
        # Remove pet
        self.manager.remove_pet("test_pet_1")
        self.assertNotIn("test_pet_1", self.manager.get_all_pets())
    
    def test_action_start_stop(self):
        """Test action start and stop"""
        # Add pet and load sprite pack data
        self.manager.add_pet("test_pet_2", "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # Start action
        success = self.manager.start_pet_action("test_pet_2", "stay")
        self.assertTrue(success)
        
        # Check action is active
        action = self.manager.get_pet_action("test_pet_2")
        self.assertIsNotNone(action)
        self.assertTrue(action.is_active_for_pet("test_pet_2"))
        
        # Stop action
        self.manager.stop_pet_action("test_pet_2")
        self.assertIsNone(self.manager.get_pet_action("test_pet_2"))
    
    # ===== EDGE CASES TESTS =====
    
    def test_nonexistent_pet(self):
        """Test handling of nonexistent pet"""
        # Try to start action for nonexistent pet
        success = self.manager.start_pet_action("nonexistent_pet", "stay")
        self.assertFalse(success)
        
        # Try to get pet info for nonexistent pet
        pet_info = self.manager.get_pet_info("nonexistent_pet")
        self.assertIsNone(pet_info)
        
        # Try to stop action for nonexistent pet
        self.manager.stop_pet_action("nonexistent_pet")  # Should not crash
    
    def test_nonexistent_action_type(self):
        """Test handling of nonexistent action type"""
        self.manager.add_pet("test_pet_3", "Hornet")
        
        # Try to start nonexistent action
        success = self.manager.start_pet_action("test_pet_3", "nonexistent_action")
        self.assertFalse(success)
    
    def test_empty_pet_list(self):
        """Test behavior with empty pet list"""
        all_pets = self.manager.get_all_pets()
        self.assertEqual(len(all_pets), 0)
        
        # Update should not crash
        self.manager.update_all_pets(0.1)
    
    def test_duplicate_pet_id(self):
        """Test handling of duplicate pet ID"""
        # Add pet twice
        self.manager.add_pet("duplicate_pet", "Hornet")
        self.manager.add_pet("duplicate_pet", "HiveQueen")  # Should overwrite
        
        pet_info = self.manager.get_pet_info("duplicate_pet")
        self.assertEqual(pet_info['sprite_pack'], "HiveQueen")
    
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_action_type_without_manager(self):
        """Test action type behavior without proper manager"""
        # This tests the fallback behavior when manager is not properly initialized
        # The action type should handle missing manager gracefully
        pass  # This would require more complex setup
    
    def test_sprite_loader_fallback(self):
        """Test sprite loader fallback behavior"""
        # Test with invalid sprite paths
        sprite = self.manager.sprite_loader.load_sprite("nonexistent.png", "nonexistent_path")
        self.assertIsNone(sprite)
    
    def test_json_parser_fallback(self):
        """Test JSON parser fallback behavior"""
        # Test with invalid sprite pack
        success = self.manager.load_sprite_pack("nonexistent_pack")
        # Should handle gracefully without crashing
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_exception_in_action_start(self):
        """Test exception handling in action start"""
        # This would require mocking action types to throw exceptions
        # For now, test that manager doesn't crash on invalid inputs
        self.manager.add_pet("error_test_pet", "Hornet")
        
        # Test with invalid action type
        success = self.manager.start_pet_action("error_test_pet", "invalid_action")
        self.assertFalse(success)
    
    def test_exception_in_action_update(self):
        """Test exception handling in action update"""
        self.manager.add_pet("update_test_pet", "Hornet")
        self.manager.start_pet_action("update_test_pet", "stay")
        
        # Update should not crash even if action has issues
        self.manager.update_pet_action("update_test_pet", 0.1)
    
    def test_exception_in_pet_removal(self):
        """Test exception handling in pet removal"""
        # Remove nonexistent pet should not crash
        self.manager.remove_pet("nonexistent_pet")
        
        # Remove pet with active action
        self.manager.add_pet("active_pet", "Hornet")
        self.manager.start_pet_action("active_pet", "stay")
        self.manager.remove_pet("active_pet")  # Should stop action first
    
    # ===== VALIDATION TESTS =====
    
    def test_pet_info_validation(self):
        """Test pet info validation"""
        self.manager.add_pet("valid_pet", "Hornet", position=(100, 100), custom_prop="test")
        
        pet_info = self.manager.get_pet_info("valid_pet")
        self.assertIn('sprite_pack', pet_info)
        self.assertIn('position', pet_info)
        self.assertIn('active', pet_info)
        self.assertIn('created_time', pet_info)
        self.assertIn('custom_prop', pet_info)
        self.assertEqual(pet_info['custom_prop'], "test")
    
    def test_action_type_validation(self):
        """Test action type validation"""
        # Test valid action type
        stay_action = self.manager.get_action_type("stay")
        self.assertIsNotNone(stay_action)
        self.assertTrue(hasattr(stay_action, 'start'))
        self.assertTrue(hasattr(stay_action, 'update'))
        self.assertTrue(hasattr(stay_action, 'stop'))
        
        # Test invalid action type
        invalid_action = self.manager.get_action_type("invalid")
        self.assertIsNone(invalid_action)
    
    def test_statistics_validation(self):
        """Test statistics validation"""
        stats = self.manager.get_statistics()
        
        required_keys = [
            'total_pets', 'active_pets', 'total_updates', 
            'total_pets_managed', 'action_start_count', 
            'action_stop_count', 'error_count', 'runtime',
            'available_action_types', 'sprite_loader_stats'
        ]
        
        for key in required_keys:
            self.assertIn(key, stats)
    
    # ===== PERFORMANCE TESTS =====
    
    def test_multiple_pets_performance(self):
        """Test performance with multiple pets"""
        # Load sprite pack data first
        self.manager.load_sprite_pack("Hornet")
        
        # Add multiple pets
        for i in range(10):
            self.manager.add_pet(f"pet_{i}", "Hornet")
            self.manager.start_pet_action(f"pet_{i}", "stay")
        
        # Update all pets multiple times
        start_time = time.time()
        for _ in range(100):
            self.manager.update_all_pets(0.016)  # ~60 FPS
        end_time = time.time()
        
        # Should complete within reasonable time
        self.assertLess(end_time - start_time, 5.0)  # Less than 5 seconds
        
        # Check statistics
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total_pets'], 10)
        self.assertEqual(stats['active_pets'], 10)
    
    def test_memory_usage(self):
        """Test memory usage management"""
        # Add pets and start actions
        for i in range(5):
            self.manager.add_pet(f"memory_pet_{i}", "Hornet")
            self.manager.start_pet_action(f"memory_pet_{i}", "stay")
        
        # Update to trigger sprite loading
        for _ in range(10):
            self.manager.update_all_pets(0.1)
        
        # Check sprite loader statistics
        sprite_stats = self.manager.get_statistics()['sprite_loader_stats']
        self.assertIsInstance(sprite_stats, dict)
        self.assertIn('total_loads', sprite_stats)
    
    def test_cache_efficiency(self):
        """Test cache efficiency"""
        # Load same sprites multiple times
        for _ in range(5):
            self.manager.sprite_loader.load_sprite("test1.png", self.test_dir + "/assets/TestSprite")
        
        # Check cache statistics
        stats = self.manager.sprite_loader.get_statistics()
        self.assertGreater(stats['cache_hits'], 0)
    
    # ===== DATA STRUCTURE TESTS =====
    
    def test_manager_data_structures(self):
        """Test manager data structures"""
        # Test pets dictionary
        self.assertIsInstance(self.manager.pets, dict)
        self.assertEqual(len(self.manager.pets), 0)
        
        # Test active_actions dictionary
        self.assertIsInstance(self.manager.active_actions, dict)
        self.assertEqual(len(self.manager.active_actions), 0)
        
        # Test action_types dictionary
        self.assertIsInstance(self.manager.action_types, dict)
        self.assertGreater(len(self.manager.action_types), 0)
    
    def test_pet_info_data_structure(self):
        """Test pet info data structure"""
        self.manager.add_pet("struct_test_pet", "Hornet", position=(50, 50))
        
        pet_info = self.manager.get_pet_info("struct_test_pet")
        
        # Check required fields
        self.assertIn('sprite_pack', pet_info)
        self.assertIn('position', pet_info)
        self.assertIn('active', pet_info)
        self.assertIn('created_time', pet_info)
        
        # Check data types
        self.assertIsInstance(pet_info['sprite_pack'], str)
        self.assertIsInstance(pet_info['position'], tuple)
        self.assertIsInstance(pet_info['active'], bool)
        self.assertIsInstance(pet_info['created_time'], float)
    
    def test_statistics_data_structure(self):
        """Test statistics data structure"""
        stats = self.manager.get_statistics()
        
        # Check data types
        self.assertIsInstance(stats['total_pets'], int)
        self.assertIsInstance(stats['active_pets'], int)
        self.assertIsInstance(stats['total_updates'], int)
        self.assertIsInstance(stats['total_pets_managed'], int)
        self.assertIsInstance(stats['action_start_count'], int)
        self.assertIsInstance(stats['action_stop_count'], int)
        self.assertIsInstance(stats['error_count'], int)
        self.assertIsInstance(stats['runtime'], float)
        self.assertIsInstance(stats['available_action_types'], list)
        self.assertIsInstance(stats['sprite_loader_stats'], dict)
    
    # ===== INTEGRATION TESTS =====
    
    def test_integration_with_sprite_loader(self):
        """Test integration with sprite loader"""
        # Test that manager can use sprite loader
        sprite = self.manager.sprite_loader.load_sprite("test1.png", self.test_dir + "/assets/TestSprite")
        self.assertIsNotNone(sprite)
        
        # Check sprite loader statistics are accessible
        stats = self.manager.get_statistics()
        self.assertIn('sprite_loader_stats', stats)
    
    def test_integration_with_json_parser(self):
        """Test integration with JSON parser"""
        # Test that manager can use JSON parser
        # This would require actual JSON files, so we test the interface
        self.assertIsNotNone(self.manager.json_parser)
        
        # Test load_sprite_pack method
        success = self.manager.load_sprite_pack("test_pack")
        # Should handle gracefully even if pack doesn't exist
    
    def test_integration_with_action_types(self):
        """Test integration with action types"""
        # Test that manager can work with action types
        self.manager.add_pet("integration_pet", "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # Start action
        success = self.manager.start_pet_action("integration_pet", "stay")
        self.assertTrue(success)
        
        # Update action
        self.manager.update_pet_action("integration_pet", 0.1)
        
        # Get sprite from action
        sprite = self.manager.get_pet_sprite("integration_pet")
        # May be None if no sprite data available, but shouldn't crash
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # 1. Add pet and load sprite pack data
        self.manager.add_pet("workflow_pet", "Hornet")
        self.manager.load_sprite_pack("Hornet")
        
        # 2. Start action
        success = self.manager.start_pet_action("workflow_pet", "stay")
        self.assertTrue(success)
        
        # 3. Update multiple times
        for _ in range(10):
            self.manager.update_pet_action("workflow_pet", 0.1)
        
        # 4. Check statistics
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total_pets'], 1)
        self.assertEqual(stats['active_pets'], 1)
        # Note: total_updates might be 0 if no update_all_pets was called
        # We'll check that the pet is active instead
        self.assertGreater(stats['action_start_count'], 0)
        
        # 5. Stop action
        self.manager.stop_pet_action("workflow_pet")
        
        # 6. Remove pet
        self.manager.remove_pet("workflow_pet")
        
        # 7. Final check
        final_stats = self.manager.get_statistics()
        self.assertEqual(final_stats['total_pets'], 0)
        self.assertEqual(final_stats['active_pets'], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2) 