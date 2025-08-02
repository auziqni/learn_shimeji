#!/usr/bin/env python3
"""
test/stay_animation_run.py - Simple Runner for Stay Animation

Simple script to run stay animation with minimal setup.
Demonstrates stay animation functionality and performance.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set display environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from animation.action_types.stay_animation import StayAnimation
from animation.animation_manager import AnimationManager


def main():
    """Main function to run stay animation"""
    pygame_initialized = False
    try:
        print("🚀 Initializing Stay Animation...")
        
        # Initialize pygame (no display needed with dummy driver)
        try:
            pygame.init()
            pygame_initialized = True
        except Exception as e:
            print(f"⚠️  Pygame initialization warning: {e}")
        
        # Initialize animation manager
        manager = AnimationManager(max_cache_size=100, max_memory_mb=50.0)
        
        # Initialize stay animation
        stay_animation = StayAnimation(manager)
        
        print("✅ Stay Animation initialized successfully")
        print(f"🎬 Action name: {stay_animation.get_action_name()}")
        
        # Load sprite pack data
        print(f"\n📦 Loading sprite pack data...")
        success = manager.load_sprite_pack("Hornet")
        if success:
            print("✅ Sprite pack data loaded successfully")
        else:
            print("⚠️  Sprite pack data loading failed (continuing with demo)")
        
        # Get animation information per sprite pack (only stay type)
        print(f"\n📊 Animation Information per Sprite Pack (Stay Type Only):")
        sprite_packs = ["Hornet", "HiveQueen", "HiveKnight"]
        
        for pack_name in sprite_packs:
            try:
                actions = manager.json_parser.get_actions(pack_name)
                if actions:
                    # Filter only stay type actions
                    stay_actions = {}
                    for action_name, action_data in actions.items():
                        action_type = getattr(action_data, 'action_type', 'Unknown')
                        if action_type.lower() == 'stay':
                            stay_actions[action_name] = action_data
                    
                    if stay_actions:
                        print(f"   🎭 {pack_name}:")
                        print(f"      📋 Stay actions found: {len(stay_actions)}")
                        
                        # Show details for each stay action
                        for action_name, action_data in stay_actions.items():
                            print(f"      🎬 Action: {action_name}")
                            
                            # Check for animations in the action data (JSONParser structure)
                            total_frames = 0
                            sprite_files = set()
                            sound_files = set()
                            
                            # Check default animation
                            if action_data.default_animation:
                                total_frames += len(action_data.default_animation.frames)
                                for frame in action_data.default_animation.frames:
                                    if frame.image:
                                        sprite_files.add(frame.image)
                                    if frame.sound:
                                        sound_files.add(frame.sound)
                            
                            # Check animation blocks
                            if action_data.animation_blocks:
                                for block in action_data.animation_blocks:
                                    total_frames += len(block.frames)
                                    for frame in block.frames:
                                        if frame.image:
                                            sprite_files.add(frame.image)
                                        if frame.sound:
                                            sound_files.add(frame.sound)
                            
                            if total_frames > 0:
                                print(f"         📦 Animation blocks: {len(action_data.animation_blocks)}")
                                print(f"         🖼️  Total frames: {total_frames}")
                                print(f"         🎨 Sprite files: {len(sprite_files)} files")
                                print(f"         🔊 Sound files: {len(sound_files)} files")
                                
                                if sprite_files:
                                    print(f"         📁 Sprites: {list(sprite_files)[:3]}{'...' if len(sprite_files) > 3 else ''}")
                                if sound_files:
                                    print(f"         🎵 Sounds: {list(sound_files)[:3]}{'...' if len(sound_files) > 3 else ''}")
                            else:
                                print(f"         ⚠️  No animations found")
                    else:
                        print(f"   ⚠️  {pack_name}: No stay type actions found")
                else:
                    print(f"   ⚠️  {pack_name}: No actions found")
            except Exception as e:
                print(f"   ❌ {pack_name}: Error loading data - {e}")
        
        # Demo: Add pet
        print(f"\n🐾 Adding demo pet...")
        manager.add_pet("demo_pet", "Hornet", position=(100, 100))
        print(f"✅ Added pet: demo_pet")
        
        # Demo: Start stay animation
        print(f"\n🎬 Starting stay animation...")
        success = stay_animation.start("demo_pet")
        if success:
            print("✅ Stay animation started successfully")
        else:
            print("❌ Failed to start stay animation")
            return 1
        
        # Demo: Update animation
        print(f"\n🔄 Updating animation...")
        
        # Update for several frames
        for frame in range(1, 6):
            print(f"   Frame {frame}: Updating stay animation...")
            stay_animation.update("demo_pet", 0.1)  # 100ms per frame
            
            # Show current sprite
            sprite = stay_animation.get_current_sprite()
            if sprite:
                print(f"      📱 Current sprite: {sprite.get_size()}")
            else:
                print(f"      ⚠️  No sprite available")
            
            # Show frame data
            frame_data = stay_animation.get_current_frame_data()
            if frame_data:
                print(f"      📊 Frame data: {frame_data.image} ({frame_data.duration}s)")
            else:
                print(f"      ⚠️  No frame data available")
        
        # Demo: Performance statistics
        print(f"\n📈 Performance Statistics:")
        stats = stay_animation.get_performance_stats()
        
        print(f"   ⏱️  Total runtime: {stats['total_runtime']:.2f}s")
        print(f"   🖼️  Frame count: {stats['frame_count']}")
        print(f"   📦 Sprite loads: {stats['sprite_load_count']}")
        print(f"   🔊 Sound plays: {stats['sound_play_count']}")
        print(f"   🎬 Current frame: {stats['current_frame']}")
        print(f"   📊 Total frames: {stats['total_frames']}")
        
        # Demo: Action state
        print(f"\n🎭 Action State:")
        print(f"   🎬 Action name: {stay_animation.get_action_name()}")
        print(f"   ✅ Is active: {stay_animation.is_active}")
        print(f"   🐾 Current pet: {stay_animation.get_current_pet_id()}")
        print(f"   🔄 Is finished: {stay_animation.is_finished()}")
        print(f"   ⏱️  Runtime: {stay_animation.get_runtime():.2f}s")
        
        # Demo: Settings
        print(f"\n⚙️  Animation Settings:")
        print(f"   🔊 Sound enabled: {stay_animation.sound_enabled}")
        print(f"   🔊 Sound volume: {stay_animation.sound_volume}")
        print(f"   ⏱️  Frame duration: {stay_animation.frame_duration:.3f}s")
        print(f"   🔄 Is looping: {stay_animation.is_looping}")
        
        # Demo: State data
        print(f"\n📊 State Data:")
        stay_animation.set_state_data("demo_key", "demo_value")
        state_data = stay_animation.get_state_data()
        print(f"   📋 State data: {state_data}")
        
        # Demo: Settings changes
        print(f"\n🔧 Testing Settings Changes:")
        
        # Change sound settings
        stay_animation.set_sound_enabled(False)
        print(f"   🔊 Sound disabled: {not stay_animation.sound_enabled}")
        
        stay_animation.set_sound_volume(0.5)
        print(f"   🔊 Volume set to 50%: {stay_animation.sound_volume == 0.5}")
        
        # Change frame duration
        stay_animation.set_frame_duration(0.05)
        print(f"   ⏱️  Frame duration changed: {stay_animation.frame_duration == 0.05}")
        
        # Change looping
        stay_animation.set_looping(False)
        print(f"   🔄 Looping disabled: {not stay_animation.is_looping}")
        
        # Demo: Multiple updates
        print(f"\n🔄 Multiple Updates Test:")
        for i in range(10):
            stay_animation.update("demo_pet", 0.05)
        
        final_stats = stay_animation.get_performance_stats()
        print(f"   📊 Final frame count: {final_stats['frame_count']}")
        print(f"   ⏱️  Final runtime: {final_stats['total_runtime']:.2f}s")
        
        # Demo: Stop animation
        print(f"\n🛑 Stopping animation...")
        stay_animation.stop("demo_pet")
        
        # Final state check
        print(f"\n📋 Final State:")
        print(f"   ✅ Is active: {stay_animation.is_active}")
        print(f"   🐾 Current pet: {stay_animation.get_current_pet_id()}")
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        manager.cleanup()
        
        print(f"\n✅ Stay Animation demo completed successfully")
        
        # Clean up pygame
        if pygame_initialized:
            pygame.quit()
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Clean up pygame on error
        if pygame_initialized:
            pygame.quit()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 