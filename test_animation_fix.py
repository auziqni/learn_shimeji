#!/usr/bin/env python3
"""
Test Animation Fix
=================

Simple test untuk menguji perbaikan animasi
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

def test_animation_fix():
    """Test perbaikan animasi"""
    print("🔧 Testing Animation Fix...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Initialize components
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True, more_data_show=False)
    sprite_loader = SpriteLoader()
    
    # Load sprite packs
    print("📦 Loading sprite packs...")
    sprite_status = json_parser.load_all_sprite_packs()
    
    if "Hornet" not in sprite_status:
        print("❌ Hornet sprite pack not available")
        return False
    
    # Test animation manager
    print("🎭 Testing animation manager...")
    anim_manager = AnimationManager("Hornet", "Animate", sprite_loader)
    
    if not anim_manager.load_sprite_data(json_parser):
        print("❌ Failed to load sprite data")
        return False
    
    # Find a multi-frame action
    actions = anim_manager.get_available_actions()
    test_action = None
    
    for action in actions:
        if anim_manager.set_action(action):
            if len(anim_manager.current_frames) > 1:
                test_action = action
                break
    
    if not test_action:
        print("❌ No multi-frame actions found")
        return False
    
    print(f"✅ Testing action: {test_action}")
    print(f"Frames: {len(anim_manager.current_frames)}")
    print(f"Durations: {anim_manager.frame_durations}")
    print(f"Is animating: {anim_manager.is_animating}")
    
    # Test animation loop
    print("\n🔄 Testing animation loop...")
    frame_changes = 0
    last_frame = anim_manager.current_frame
    
    for i in range(120):  # 2 seconds at 60 FPS
        delta_time = 1.0 / 60.0
        
        # Update animation
        anim_manager.update_animation(delta_time)
        
        # Check for frame changes
        if anim_manager.current_frame != last_frame:
            frame_changes += 1
            print(f"Frame change {frame_changes}: {last_frame} -> {anim_manager.current_frame}")
            last_frame = anim_manager.current_frame
        
        # Draw to screen
        screen.fill((0, 0, 0))
        current_image = anim_manager.get_current_image()
        if current_image:
            screen.blit(current_image, (400, 300))
        pygame.display.flip()
        
        clock.tick(60)
    
    print(f"\n📊 Results:")
    print(f"Frame changes: {frame_changes}")
    print(f"Expected changes: ~{sum(anim_manager.frame_durations) / 0.1:.0f}")
    
    if frame_changes > 0:
        print("✅ Animation is working!")
    else:
        print("❌ Animation not working")
    
    pygame.quit()
    return frame_changes > 0

if __name__ == "__main__":
    print("🚀 Animation Fix Test")
    print("=" * 30)
    
    try:
        success = test_animation_fix()
        if success:
            print("\n✅ Animation fix successful!")
        else:
            print("\n❌ Animation fix failed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 