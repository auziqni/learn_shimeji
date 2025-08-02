#!/usr/bin/env python3
"""
test/test_animation_integration.py - Test integration between animation.py and json_parser.py

This test demonstrates how the refactored animation system works with JSON parser data.
"""

import sys
import os
import pygame
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.json_parser import JSONParser
from animation import AnimationManager, Animation, get_global_sprite_cache_size, get_global_sound_cache_size


def test_animation_integration():
    """Test the integration between animation system and JSON parser"""
    
    print("🧪 Testing Animation System Integration with JSON Parser")
    print("=" * 60)
    
    # Initialize pygame
    pygame.init()
    
    # Initialize JSON parser with correct assets path
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True, more_data_show=True)
    
    # Load sprite packs
    sprite_packs = json_parser.load_all_sprite_packs()
    json_parser.print_summary()
    
    # Initialize animation manager
    animation_manager = AnimationManager(json_parser)
    
    # Get ready sprites
    ready_sprites = json_parser.get_ready_sprite_names()
    print(f"\n🎬 Ready sprites: {ready_sprites}")
    
    if not ready_sprites:
        print("❌ No ready sprites found!")
        return False
    
    # Test with first ready sprite
    test_sprite = ready_sprites[0]
    print(f"\n🎭 Testing with sprite: {test_sprite}")
    
    # Load animations for test sprite
    success = animation_manager.load_sprite_animations(test_sprite)
    if not success:
        print(f"❌ Failed to load animations for {test_sprite}")
        return False
    
    # Get available actions
    actions = animation_manager.get_available_actions(test_sprite)
    print(f"✅ Loaded {len(actions)} actions for {test_sprite}")
    
    if not actions:
        print("❌ No actions available!")
        return False
    
    # Test each action
    print(f"\n🎬 Testing {len(actions)} actions:")
    for i, action_name in enumerate(actions[:5]):  # Test first 5 actions
        print(f"\n  {i+1}. Testing action: {action_name}")
        
        # Get animation
        animation = animation_manager.get_animation(test_sprite, action_name)
        if not animation:
            print(f"    ❌ Failed to get animation for {action_name}")
            continue
        
        print(f"    ✅ Animation loaded: {animation.get_animation_name()}")
        print(f"    📊 Frame count: {animation.get_frame_count()}")
        
        # Test animation properties
        if animation.get_frame_count() > 0:
            print(f"    🎵 Sound enabled: {animation.get_sound_enabled()}")
            print(f"    🔄 Looping: {animation.is_looping}")
            
            # Test animation playback
            animation.play()
            print(f"    ▶️  Started animation")
            
            # Simulate a few frames
            for frame in range(min(5, animation.get_frame_count())):
                animation.update(1.0/30.0)  # 30 FPS
                current_frame = animation.get_current_frame()
                if current_frame:
                    velocity = animation.get_current_velocity()
                    print(f"      Frame {frame+1}: velocity={velocity}")
            
            animation.stop()
            print(f"    ⏹️  Stopped animation")
        else:
            print(f"    ⚠️  No frames in animation")
    
    # Test pet animation management
    print(f"\n🐾 Testing pet animation management:")
    
    # Start animation for a test pet
    test_pet_id = "test_pet_001"
    test_action = actions[0]
    
    success = animation_manager.start_animation(test_pet_id, test_sprite, test_action)
    if success:
        print(f"  ✅ Started animation for pet {test_pet_id}")
        
        # Get pet animation
        pet_animation = animation_manager.get_pet_animation(test_pet_id)
        if pet_animation:
            print(f"  📊 Pet animation: {pet_animation.get_animation_name()}")
            print(f"  🎬 Frame count: {pet_animation.get_frame_count()}")
            
            # Update pet animation
            for i in range(3):
                animation_manager.update_pet_animation(test_pet_id, 1.0/30.0)
                current_frame = pet_animation.get_current_frame()
                if current_frame:
                    print(f"    Frame {i+1}: velocity={pet_animation.get_current_velocity()}")
            
            # Stop pet animation
            animation_manager.stop_pet_animation(test_pet_id)
            print(f"  ⏹️  Stopped pet animation")
        else:
            print(f"  ❌ Failed to get pet animation")
    else:
        print(f"  ❌ Failed to start animation for pet {test_pet_id}")
    
    # Test cache management
    print(f"\n💾 Testing cache management:")
    sprite_cache_size = get_global_sprite_cache_size()
    sound_cache_size = get_global_sound_cache_size()
    print(f"  🖼️  Sprite cache size: {sprite_cache_size}")
    print(f"  🔊 Sound cache size: {sound_cache_size}")
    
    # Cleanup
    animation_manager.cleanup()
    print(f"\n🧹 Cleanup completed")
    
    return True


def test_animation_performance():
    """Test animation system performance with multiple pets"""
    
    print("\n🚀 Testing Animation System Performance")
    print("=" * 50)
    
    # Initialize systems
    pygame.init()
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True)
    animation_manager = AnimationManager(json_parser)
    
    # Load sprite packs
    sprite_packs = json_parser.load_all_sprite_packs()
    ready_sprites = json_parser.get_ready_sprite_names()
    
    if not ready_sprites:
        print("❌ No sprites available for performance test")
        return False
    
    # Load animations for first sprite
    test_sprite = ready_sprites[0]
    animation_manager.load_sprite_animations(test_sprite)
    actions = animation_manager.get_available_actions(test_sprite)
    
    if not actions:
        print("❌ No actions available for performance test")
        return False
    
    # Test with multiple pets
    num_pets = 5
    test_action = actions[0]
    
    print(f"🎭 Creating {num_pets} pets with animation: {test_action}")
    
    start_time = time.time()
    
    # Create pets
    for i in range(num_pets):
        pet_id = f"performance_pet_{i:03d}"
        success = animation_manager.start_animation(pet_id, test_sprite, test_action)
        if success:
            print(f"  ✅ Created pet {pet_id}")
        else:
            print(f"  ❌ Failed to create pet {pet_id}")
    
    # Update all pets
    update_time = time.time()
    for frame in range(30):  # 30 frames
        for i in range(num_pets):
            pet_id = f"performance_pet_{i:03d}"
            animation_manager.update_pet_animation(pet_id, 1.0/30.0)
    
    end_time = time.time()
    
    # Performance metrics
    creation_time = update_time - start_time
    update_time_total = end_time - update_time
    total_time = end_time - start_time
    
    print(f"\n📊 Performance Results:")
    print(f"  ⏱️  Pet creation time: {creation_time:.3f}s")
    print(f"  ⏱️  Animation update time: {update_time_total:.3f}s")
    print(f"  ⏱️  Total time: {total_time:.3f}s")
    print(f"  🎬 Frames per second: {30/update_time_total:.1f}")
    
    # Cleanup
    for i in range(num_pets):
        pet_id = f"performance_pet_{i:03d}"
        animation_manager.stop_pet_animation(pet_id)
    
    animation_manager.cleanup()
    print(f"🧹 Performance test cleanup completed")
    
    return True


if __name__ == "__main__":
    print("🎬 Animation Integration Test Suite")
    print("=" * 40)
    
    # Run integration test
    success1 = test_animation_integration()
    
    # Run performance test
    success2 = test_animation_performance()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    pygame.quit() 