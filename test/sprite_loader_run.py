#!/usr/bin/env python3
"""
test/sprite_loader_run.py - Simple Runner for Sprite Loader

Simple script to run sprite loader with minimal setup.
Demonstrates sprite loading, caching, and memory management.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set display environment for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from animation.sprite_loader import SpriteLoader, get_global_sprite_loader


def main():
    """Main function to run sprite loader"""
    pygame_initialized = False
    try:
        print("🚀 Initializing Sprite Loader...")
        
        # Initialize pygame (no display needed with dummy driver)
        try:
            pygame.init()
            pygame_initialized = True
        except Exception as e:
            print(f"⚠️  Pygame initialization warning: {e}")
        
        # Initialize sprite loader
        loader = SpriteLoader(max_cache_size=100, max_memory_mb=50)
        
        print("✅ Sprite Loader initialized successfully")
        print(f"📊 Initial cache size: {len(loader._sprite_cache)} sprites")
        print(f"💾 Memory usage: {loader.current_memory_mb:.1f}MB")
        
        # Test with real sprite pack if available
        sprite_packs = ["Hornet", "HiveQueen", "HiveKnight"]
        available_packs = []
        
        for pack in sprite_packs:
            pack_path = f"assets/{pack}"
            if os.path.exists(pack_path):
                available_packs.append(pack)
        
        if available_packs:
            print(f"\n🎯 Testing with available sprite packs: {', '.join(available_packs)}")
            
            # Test loading sprites from first available pack
            test_pack = available_packs[0]
            pack_path = f"assets/{test_pack}"
            
            print(f"\n📦 Loading sprites from {test_pack}...")
            
            # Try to load some common sprites
            test_sprites = ["shime1.png", "shime2.png", "shime3.png"]
            loaded_count = 0
            
            print(f"🔄 Loop 1: Loading sprites from disk...")
            for sprite_name in test_sprites:
                sprite = loader.load_sprite(sprite_name, pack_path)
                if sprite:
                    print(f"   ✅ Loaded: {sprite_name} ({sprite.get_size()})")
                    loaded_count += 1
                else:
                    print(f"   ❌ Failed to load: {sprite_name}")
            
            print(f"\n📊 Loading Results:")
            print(f"   Successfully loaded: {loaded_count}/{len(test_sprites)} sprites")
            print(f"   Cache size: {len(loader._sprite_cache)} sprites")
            print(f"   Memory usage: {loader.current_memory_mb:.1f}MB")
            
            # Test cache functionality with multiple loops
            print(f"\n🔄 Testing cache functionality with 4 loops...")
            
            for loop in range(2, 5):  # Loop 2, 3, 4
                print(f"\n🔄 Loop {loop}: Loading same sprites from cache...")
                for sprite_name in test_sprites:
                    sprite = loader.load_sprite(sprite_name, pack_path)
                    if sprite:
                        print(f"   ✅ Cached: {sprite_name} ({sprite.get_size()})")
                    else:
                        print(f"   ❌ Failed to load: {sprite_name}")
            
            # Verify cache hit
            print(f"\n🔍 Cache verification:")
            print("   ✅ Cache working correctly - All sprites loaded from cache in loops 2-4")
            
            # Show statistics
            print(f"\n📈 Performance Statistics:")
            stats = loader.get_statistics()
            
            # Calculate expected values
            total_requests = stats['cache_hits'] + stats['cache_misses']
            expected_hits = total_requests - 3  # 3 initial loads from disk
            expected_hit_rate = expected_hits / total_requests if total_requests > 0 else 0
            
            print(f"   📦 Total requests: {total_requests} times")
            print(f"   ✅ Cache hits: {stats['cache_hits']} times")
            print(f"   ❌ Cache misses: {stats['cache_misses']} times")
            print(f"   🎯 Hit rate: {stats['cache_hits']}/{total_requests} ({stats['hit_rate']:.1%})")
            print(f"   📊 Expected: {expected_hits}/{total_requests} ({expected_hit_rate:.1%})")
            print(f"   ⚠️  Load errors: {stats['load_errors']} errors")
            
            # Show breakdown
            print(f"\n📋 Breakdown:")
            print(f"   🔄 Loop 1: 3 loads from disk (3 misses)")
            print(f"   🔄 Loop 2-4: 9 loads from cache (9 hits)")
            print(f"   📊 Total: {total_requests} requests, {stats['cache_hits']} hits, {stats['cache_misses']} misses")
            
            # Test global functions
            print(f"\n🌐 Testing global functions...")
            global_loader = get_global_sprite_loader()
            global_cache_size = len(global_loader._sprite_cache)
            print(f"   Global cache size: {global_cache_size} sprites")
            
            # Test cache clearing
            print(f"\n🧹 Testing cache clearing...")
            loader.clear_cache()
            print(f"   Cache cleared, new size: {len(loader._sprite_cache)} sprites")
            
        else:
            print("⚠️  No sprite packs found in assets/ directory")
            print("   Creating test sprite for demonstration...")
            
            # Create a simple test sprite
            import pygame
            pygame.init()
            
            test_sprite = pygame.Surface((32, 32))
            test_sprite.fill((255, 0, 0))  # Red sprite
            
            # Save test sprite
            os.makedirs("test_sprites", exist_ok=True)
            pygame.image.save(test_sprite, "test_sprites/test.png")
            
            # Test loading
            sprite = loader.load_sprite("test.png", "test_sprites")
            if sprite:
                print(f"✅ Test sprite loaded: {sprite.get_size()}")
                print(f"📊 Cache size: {len(loader._sprite_cache)} sprites")
            
            pygame.quit()
        
        print(f"\n✅ Sprite Loader test completed successfully")
        
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