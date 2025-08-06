#!/usr/bin/env python3
"""
Debug Animation System
=====================

Script untuk debug dan menguji sistem animasi
"""

import sys
import os
import pygame
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.json_parser import JSONParser
from src.animation.animation_manager import AnimationManager
from src.animation.sprite_loader import SpriteLoader
from src.utils.log_manager import get_logger

def test_animation_system():
    """Test animation system secara terpisah"""
    print("🔍 Testing Animation System...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Initialize components
    logger = get_logger("debug_animation")
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=False, more_data_show=True)
    sprite_loader = SpriteLoader()
    
    # Load sprite packs
    print("\n📦 Loading sprite packs...")
    sprite_status = json_parser.load_all_sprite_packs()
    print(f"Sprite status: {sprite_status}")
    
    if "Hornet" not in sprite_status or sprite_status["Hornet"] != "READY":
        print("❌ Hornet sprite pack not ready!")
        return False
    
    # Test different action types
    action_types = ["Stay", "Move", "Animate", "Behavior", "Embedded"]
    
    for action_type in action_types:
        print(f"\n🎭 Testing action type: {action_type}")
        
        # Create animation manager
        anim_manager = AnimationManager("Hornet", action_type, sprite_loader)
        
        # Load sprite data
        if not anim_manager.load_sprite_data(json_parser):
            print(f"❌ Failed to load sprite data for {action_type}")
            continue
        
        # Get available actions
        actions = anim_manager.get_available_actions()
        print(f"Available actions: {len(actions)}")
        
        if not actions:
            print(f"⚠️ No actions found for {action_type}")
            continue
        
        # Test first action
        first_action = actions[0]
        print(f"Testing action: {first_action}")
        
        if anim_manager.set_action(first_action):
            frames = len(anim_manager.current_frames)
            durations = len(anim_manager.frame_durations)
            print(f"Loaded {frames} frames with {durations} durations")
            
            # Test animation loop
            print("🔄 Testing animation loop...")
            start_time = time.time()
            frame_count = 0
            
            for i in range(60):  # 60 frames at 60 FPS = 1 second
                delta_time = 1.0 / 60.0  # 16.67ms
                
                # Update animation
                anim_manager.update_animation(delta_time)
                
                # Get current image
                current_image = anim_manager.get_current_image()
                if current_image:
                    frame_count += 1
                    
                    # Draw to screen
                    screen.fill((0, 0, 0))
                    screen.blit(current_image, (400, 300))
                    pygame.display.flip()
                
                clock.tick(60)
            
            elapsed_time = time.time() - start_time
            print(f"Animation test completed in {elapsed_time:.2f}s")
            print(f"Frame updates: {frame_count}")
            
            # Check if animation actually changed frames
            if frames > 1:
                print("✅ Multi-frame animation working")
            else:
                print("⚠️ Single frame animation (static)")
        else:
            print(f"❌ Failed to set action {first_action}")
    
    pygame.quit()
    return True

def test_frame_timing():
    """Test frame timing issues"""
    print("\n⏱️ Testing frame timing...")
    
    # Initialize components
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=False, more_data_show=True)
    sprite_loader = SpriteLoader()
    
    # Load sprite data
    sprite_status = json_parser.load_all_sprite_packs()
    
    if "Hornet" not in sprite_status:
        print("❌ Hornet sprite pack not available")
        return False
    
    # Test animation manager with Animate type (should have multi-frame animations)
    anim_manager = AnimationManager("Hornet", "Animate", sprite_loader)
    
    if not anim_manager.load_sprite_data(json_parser):
        print("❌ Failed to load sprite data")
        return False
    
    # Find an action with multiple frames
    actions = anim_manager.get_available_actions()
    multi_frame_action = None
    
    for action in actions:
        if anim_manager.set_action(action):
            if len(anim_manager.current_frames) > 1:
                multi_frame_action = action
                break
    
    if not multi_frame_action:
        print("❌ No multi-frame actions found")
        return False
    
    print(f"Testing multi-frame action: {multi_frame_action}")
    print(f"Frames: {len(anim_manager.current_frames)}")
    print(f"Durations: {anim_manager.frame_durations}")
    
    # Test frame timing
    print("\n📊 Frame timing analysis:")
    for i, duration in enumerate(anim_manager.frame_durations):
        print(f"Frame {i}: {duration}s")
    
    # Test animation update
    print("\n🔄 Animation update test:")
    total_duration = sum(anim_manager.frame_durations)
    print(f"Total animation duration: {total_duration}s")
    
    # Simulate animation loop
    anim_manager.animation_timer = 0
    anim_manager.current_frame = 0
    
    for step in range(10):
        delta_time = 0.1  # 100ms per step
        old_frame = anim_manager.current_frame
        
        anim_manager.update_animation(delta_time)
        
        new_frame = anim_manager.current_frame
        if new_frame != old_frame:
            print(f"Step {step}: Frame {old_frame} -> {new_frame}")
        else:
            print(f"Step {step}: Frame {old_frame} (no change)")
    
    return True

def test_sprite_loading():
    """Test sprite loading issues"""
    print("\n🖼️ Testing sprite loading...")
    
    sprite_loader = SpriteLoader()
    
    # Test loading specific sprites
    test_sprites = [
        "assets/Hornet/shimePet1.png",
        "assets/Hornet/shimePet2.png",
        "assets/Hornet/shimePet3.png"
    ]
    
    for sprite_path in test_sprites:
        sprite = sprite_loader.load_sprite(sprite_path)
        if sprite:
            print(f"✅ Loaded: {sprite_path} ({sprite.get_width()}x{sprite.get_height()})")
        else:
            print(f"❌ Failed to load: {sprite_path}")
    
    # Test cache stats
    stats = sprite_loader.get_cache_stats()
    print(f"\n📊 Cache stats: {stats}")
    
    return True

if __name__ == "__main__":
    print("🚀 Animation Debug Tool")
    print("=" * 50)
    
    try:
        # Test sprite loading
        test_sprite_loading()
        
        # Test frame timing
        test_frame_timing()
        
        # Test full animation system
        test_animation_system()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 