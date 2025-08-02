#!/usr/bin/env python3
"""
test/animation_manager_run.py - Simple Runner for Animation Manager

Simple script to run animation manager with minimal setup.
Demonstrates pet management, action types, and performance monitoring.
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
from animation.animation_manager import AnimationManager


def main():
    """Main function to run animation manager"""
    pygame_initialized = False
    try:
        print("🚀 Initializing Animation Manager...")
        
        # Initialize pygame (no display needed with dummy driver)
        try:
            pygame.init()
            pygame_initialized = True
        except Exception as e:
            print(f"⚠️  Pygame initialization warning: {e}")
        
        # Initialize animation manager
        manager = AnimationManager(max_cache_size=100, max_memory_mb=50.0)
        
        print("✅ Animation Manager initialized successfully")
        print(f"📊 Available action types: {manager.get_available_action_types()}")
        
        # Load sprite pack data
        print(f"\n📦 Loading sprite pack data...")
        success = manager.load_sprite_pack("Hornet")
        if success:
            print("✅ Sprite pack data loaded successfully")
        else:
            print("⚠️  Sprite pack data loading failed (continuing with demo)")
        
        # Demo: Add pets
        print(f"\n🐾 Adding demo pets...")
        manager.add_pet("pet_1", "Hornet", position=(100, 100))
        manager.add_pet("pet_2", "HiveQueen", position=(200, 150))
        manager.add_pet("pet_3", "HiveKnight", position=(300, 200))
        
        print(f"✅ Added {len(manager.get_all_pets())} pets")
        
        # Demo: Start actions
        print(f"\n🎬 Starting actions for pets...")
        
        # Start stay animation for all pets
        for pet_id in manager.get_all_pets():
            success = manager.start_pet_action(pet_id, "stay")
            if success:
                print(f"   ✅ Started stay action for {pet_id}")
            else:
                print(f"   ❌ Failed to start action for {pet_id}")
        
        # Demo: Update animations
        print(f"\n🔄 Updating animations...")
        
        # Update for several frames
        for frame in range(1, 6):
            print(f"   Frame {frame}: Updating all pets...")
            manager.update_all_pets(0.1)  # 100ms per frame
            
            # Show current sprites
            for pet_id in manager.get_all_pets():
                sprite = manager.get_pet_sprite(pet_id)
                if sprite:
                    print(f"      📱 {pet_id}: Sprite loaded ({sprite.get_size()})")
                else:
                    print(f"      ⚠️  {pet_id}: No sprite available")
        
        # Demo: Performance statistics
        print(f"\n📈 Performance Statistics:")
        stats = manager.get_statistics()
        
        print(f"   🐾 Total pets: {stats['total_pets']}")
        print(f"   🎬 Active pets: {stats['active_pets']}")
        print(f"   🔄 Total updates: {stats['total_updates']}")
        print(f"   ⏱️  Runtime: {stats['runtime']:.2f}s")
        print(f"   🎯 Action starts: {stats['action_start_count']}")
        print(f"   🛑 Action stops: {stats['action_stop_count']}")
        print(f"   ❌ Errors: {stats['error_count']}")
        
        # Sprite loader statistics
        sprite_stats = stats['sprite_loader_stats']
        print(f"\n📦 Sprite Loader Statistics:")
        print(f"   📦 Total loads: {sprite_stats['total_loads']}")
        print(f"   ✅ Cache hits: {sprite_stats['cache_hits']}")
        print(f"   ❌ Cache misses: {sprite_stats['cache_misses']}")
        print(f"   🎯 Hit rate: {sprite_stats['hit_rate']:.1%}")
        print(f"   💾 Memory usage: {sprite_stats.get('memory_usage_mb', 0.0):.1f}MB")
        
        # Demo: Action type information
        print(f"\n🎭 Action Type Information:")
        for action_name in manager.get_available_action_types():
            action_type = manager.get_action_type(action_name)
            if action_type:
                print(f"   🎬 {action_name}: {action_type.get_action_name()}")
                
                # Show performance stats if available
                if hasattr(action_type, 'get_performance_stats'):
                    perf_stats = action_type.get_performance_stats()
                    print(f"      📊 Runtime: {perf_stats.get('total_runtime', 0):.2f}s")
                    print(f"      🖼️  Frames: {perf_stats.get('frame_count', 0)}")
        
        # Demo: Pet management
        print(f"\n🐾 Pet Management Demo:")
        all_pets = manager.get_all_pets()
        print(f"   📋 All pets: {all_pets}")
        
        for pet_id in all_pets:
            pet_info = manager.get_pet_info(pet_id)
            action = manager.get_pet_action(pet_id)
            
            print(f"   🐾 {pet_id}:")
            print(f"      📦 Sprite pack: {pet_info['sprite_pack']}")
            print(f"      📍 Position: {pet_info['position']}")
            print(f"      🎬 Active action: {action.get_action_name() if action else 'None'}")
        
        # Demo: Cache management
        print(f"\n🧹 Cache Management:")
        print("   Clearing cache...")
        manager.clear_cache()
        
        # Final statistics
        final_stats = manager.get_statistics()
        print(f"   📊 Final sprite cache size: {final_stats['sprite_loader_stats'].get('cache_size', 0)}")
        
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        manager.cleanup()
        
        print(f"\n✅ Animation Manager demo completed successfully")
        
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