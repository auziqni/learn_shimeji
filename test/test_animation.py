import pygame
import sys
import os
import time
import unittest
from typing import List, Dict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from animation import Animation, AnimationFrame, clear_global_sprite_cache, get_global_sprite_cache_size


class TestAnimation(unittest.TestCase):
    """Comprehensive test suite for Animation system"""
    
    def setUp(self):
        """Initialize pygame and test data"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        
        # Test sprite pack path
        self.sprite_pack_path = "assets/Hornet"
        
        # Sample frame data from XML (simplified for testing)
        self.test_frames_data = [
            {
                'Image': 'shime1.png',
                'ImageAnchor': '64,128',
                'Velocity': '0,0',
                'Duration': '75'
            },
            {
                'Image': 'shime1a.png',
                'ImageAnchor': '64,128',
                'Velocity': '0,0',
                'Duration': '5'
            }
        ]
        
        # Walk animation data
        self.walk_frames_data = [
            {
                'Image': 'shime2.png',
                'ImageAnchor': '64,128',
                'Velocity': '-2,0',
                'Duration': '4'
            },
            {
                'Image': 'shime3.png',
                'ImageAnchor': '64,128',
                'Velocity': '-2,0',
                'Duration': '4'
            },
            {
                'Image': 'shime3a.png',
                'ImageAnchor': '64,128',
                'Velocity': '-2,0',
                'Duration': '4'
            }
        ]
    
    def tearDown(self):
        """Clean up after tests"""
        clear_global_sprite_cache()
        pygame.quit()
    
    def test_animation_creation(self):
        """Test basic animation creation"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        self.assertEqual(animation.get_animation_name(), "Test")
        self.assertGreater(animation.get_frame_count(), 0)
        self.assertFalse(animation.is_playing)
    
    def test_sprite_loading(self):
        """Test sprite loading and caching"""
        # Clear cache first
        clear_global_sprite_cache()
        initial_cache_size = get_global_sprite_cache_size()
        
        # Create animation
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        # Check if sprites were loaded
        self.assertGreater(animation.get_frame_count(), 0)
        
        # Check if sprites are valid pygame surfaces
        current_frame = animation.get_current_frame()
        self.assertIsNotNone(current_frame)
        self.assertIsInstance(current_frame.image, pygame.Surface)
        
        # Check cache size increased
        final_cache_size = get_global_sprite_cache_size()
        self.assertGreater(final_cache_size, initial_cache_size)
    
    def test_frame_timing(self):
        """Test frame timing and transitions"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        # Start animation
        animation.play()
        initial_frame = animation.get_current_frame_index()
        
        # Update with small delta time (should not advance frame yet)
        animation.update(0.01)  # 10ms
        self.assertEqual(animation.get_current_frame_index(), initial_frame)
        
        # Update with enough time to advance frame (75 frames duration = 2.5 seconds at 30 FPS)
        animation.update(3.0)  # 3 seconds should advance frame
        self.assertGreater(animation.get_current_frame_index(), initial_frame)
    
    def test_animation_controls(self):
        """Test play, pause, stop controls"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        # Test play
        animation.play()
        self.assertTrue(animation.is_playing)
        self.assertEqual(animation.get_current_frame_index(), 0)
        
        # Test pause
        animation.pause()
        self.assertFalse(animation.is_playing)
        
        # Test stop
        animation.stop()
        self.assertFalse(animation.is_playing)
        self.assertEqual(animation.get_current_frame_index(), 0)
    
    def test_looping_behavior(self):
        """Test looping and non-looping animations"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        # Test looping (default)
        animation.play()
        initial_frame = animation.get_current_frame_index()
        
        # Advance to end
        for _ in range(animation.get_frame_count() + 1):
            animation.update(3.0)  # 3 seconds per update
        
        # Should loop back to start
        self.assertEqual(animation.get_current_frame_index(), 0)
        
        # Test non-looping
        animation.set_looping(False)
        animation.play()
        
        # Advance to end
        for _ in range(animation.get_frame_count() + 1):
            animation.update(3.0)  # 3 seconds per update
        
        # Should stop at last frame
        self.assertEqual(animation.get_current_frame_index(), animation.get_frame_count() - 1)
        self.assertFalse(animation.is_playing)
    
    def test_velocity_parsing(self):
        """Test velocity parsing from XML data"""
        animation = Animation(self.sprite_pack_path, "Walk", self.walk_frames_data)
        
        # Check velocity parsing
        velocity = animation.get_current_velocity()
        self.assertEqual(velocity, (-2.0, 0.0))
    
    def test_anchor_parsing(self):
        """Test anchor point parsing"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        current_frame = animation.get_current_frame()
        self.assertIsNotNone(current_frame)
        self.assertEqual(current_frame.image_anchor, (64, 128))
    
    def test_hotspot_data(self):
        """Test hotspot data handling"""
        frames_with_hotspot = [
            {
                'Image': 'shime11.png',
                'ImageAnchor': '64,128',
                'Velocity': '0,0',
                'Duration': '75',
                'Hotspot': {
                    'Shape': 'Ellipse',
                    'Origin': '48,71',
                    'Size': '17,7',
                    'Behavior': 'BePet'
                }
            }
        ]
        
        animation = Animation(self.sprite_pack_path, "Sit", frames_with_hotspot)
        hotspot = animation.get_current_hotspot()
        
        self.assertIsNotNone(hotspot)
        self.assertEqual(hotspot['Shape'], 'Ellipse')
        self.assertEqual(hotspot['Behavior'], 'BePet')
    
    def test_performance_multiple_animations(self):
        """Test performance with multiple animations (simulating 25+ pets)"""
        animations = []
        start_time = time.time()
        
        # Create 25 animations (simulating 25 pets)
        for i in range(25):
            animation = Animation(self.sprite_pack_path, f"Pet_{i}", self.test_frames_data)
            animation.play()
            animations.append(animation)
        
        creation_time = time.time() - start_time
        print(f"Created 25 animations in {creation_time:.3f} seconds")
        
        # Test update performance
        update_start = time.time()
        for _ in range(30):  # 30 frames (1 second at 30 FPS)
            for animation in animations:
                animation.update(1.0/30.0)
        update_time = time.time() - update_start
        
        print(f"Updated 25 animations for 30 frames in {update_time:.3f} seconds")
        print(f"Average time per frame: {update_time/30:.3f} seconds")
        
        # Performance assertions
        self.assertLess(creation_time, 2.0)  # Should create 25 animations quickly
        self.assertLess(update_time, 1.0)    # Should update 25 animations in under 1 second
        
        # Clean up
        for animation in animations:
            animation.cleanup()
    
    def test_memory_efficiency(self):
        """Test memory efficiency with sprite caching"""
        initial_cache_size = get_global_sprite_cache_size()
        
        # Create multiple animations using same sprites
        animations = []
        for i in range(10):
            animation = Animation(self.sprite_pack_path, f"Animation_{i}", self.test_frames_data)
            animations.append(animation)
        
        # Cache size should not increase significantly (sprites are shared)
        final_cache_size = get_global_sprite_cache_size()
        cache_increase = final_cache_size - initial_cache_size
        
        print(f"Cache size increase for 10 animations: {cache_increase}")
        
        # Should be efficient (minimal cache increase)
        self.assertLess(cache_increase, 10)  # Should reuse sprites
        
        # Clean up
        for animation in animations:
            animation.cleanup()
    
    def test_error_handling(self):
        """Test error handling for missing sprites"""
        invalid_frames_data = [
            {
                'Image': 'nonexistent.png',
                'ImageAnchor': '64,128',
                'Velocity': '0,0',
                'Duration': '75'
            }
        ]
        
        # Should not crash, should handle missing sprite gracefully
        animation = Animation(self.sprite_pack_path, "Invalid", invalid_frames_data)
        
        # Should have 0 frames (no valid sprites loaded)
        self.assertEqual(animation.get_frame_count(), 0)
    
    def test_frame_manual_control(self):
        """Test manual frame control"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        
        # Test setting frame index
        animation.set_frame_index(1)
        self.assertEqual(animation.get_current_frame_index(), 1)
        
        # Test bounds checking
        animation.set_frame_index(999)  # Invalid index
        self.assertLess(animation.get_current_frame_index(), animation.get_frame_count())
    
    def test_animation_finish_detection(self):
        """Test animation finish detection"""
        animation = Animation(self.sprite_pack_path, "Test", self.test_frames_data)
        animation.set_looping(False)
        animation.play()
        
        # Advance to end
        for _ in range(animation.get_frame_count() + 1):
            animation.update(3.0)  # 3 seconds per update
        
        # Should detect as finished
        self.assertTrue(animation.is_finished())


class TestAnimationIntegration(unittest.TestCase):
    """Integration tests with XML parser"""
    
    def setUp(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        
        # Import XML parser
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))
        from xml_parser import XMLParser
        self.xml_parser = XMLParser()
    
    def tearDown(self):
        clear_global_sprite_cache()
        pygame.quit()
    
    def test_xml_integration(self):
        """Test integration with XML parser"""
        # Load actions from XML
        actions = self.xml_parser.get_actions("Hornet")
        
        # Test creating animation from XML data
        if 'Stand' in actions:
            stand_action = actions['Stand']
            # Convert ActionData to frame format
            frames_data = []
            if stand_action.default_animation:
                for frame in stand_action.default_animation.frames:
                    frames_data.append({
                        'Image': frame.image,
                        'ImageAnchor': '64,128',
                        'Velocity': f"{frame.velocity[0]},{frame.velocity[1]}",
                        'Duration': str(int(frame.duration * 30))  # Convert to frame units
                    })
            
            animation = Animation("assets/Hornet", "Stand", frames_data)
            
            self.assertEqual(animation.get_animation_name(), "Stand")
            self.assertGreater(animation.get_frame_count(), 0)
    
    def test_multiple_xml_animations(self):
        """Test loading multiple animations from XML"""
        actions = self.xml_parser.get_actions("Hornet")
        
        animations = {}
        for action_name, action_data in actions.items():
            if action_name in ['Stand', 'Walk', 'Sit']:
                # Convert ActionData to frame format
                frames_data = []
                if action_data.default_animation:
                    for frame in action_data.default_animation.frames:
                        frames_data.append({
                            'Image': frame.image,
                            'ImageAnchor': '64,128',
                            'Velocity': f"{frame.velocity[0]},{frame.velocity[1]}",
                            'Duration': str(int(frame.duration * 30))  # Convert to frame units
                        })
                
                animation = Animation("assets/Hornet", action_name, frames_data)
                animations[action_name] = animation
        
        # Test that all animations loaded successfully
        self.assertIn('Stand', animations)
        self.assertIn('Walk', animations)
        self.assertIn('Sit', animations)
        
        # Test animation switching
        for animation in animations.values():
            animation.play()
            self.assertTrue(animation.is_playing)


def run_visual_test():
    """Run a visual test to see animations in action"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Load test animation
    test_frames = [
        {
            'Image': 'shime1.png',
            'ImageAnchor': '64,128',
            'Velocity': '0,0',
            'Duration': '75'
        },
        {
            'Image': 'shime1a.png',
            'ImageAnchor': '64,128',
            'Velocity': '0,0',
            'Duration': '5'
        }
    ]
    
    animation = Animation("assets/Hornet", "VisualTest", test_frames)
    animation.play()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    animation.pause() if animation.is_playing else animation.play()
                elif event.key == pygame.K_r:
                    animation.stop()
                    animation.play()
        
        # Update animation
        animation.update(1.0/30.0)
        
        # Draw
        screen.fill((255, 255, 255))
        
        current_frame = animation.get_current_frame()
        if current_frame:
            # Draw sprite at center of screen
            sprite = current_frame.image
            anchor = current_frame.image_anchor
            screen.blit(sprite, (400 - anchor[0], 300 - anchor[1]))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()


if __name__ == "__main__":
    # Run unit tests
    print("Running Animation Tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run visual test (optional)
    print("\nPress Enter to run visual test (or Ctrl+C to exit)...")
    try:
        input()
        run_visual_test()
    except KeyboardInterrupt:
        print("Visual test skipped.") 