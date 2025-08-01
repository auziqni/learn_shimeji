#!/usr/bin/env python3
"""
test/json_parser_run.py - Simple Runner for JSONParser

Simple script to run JSONParser with minimal setup.
Loads sprite packs from JSON files, converts XML to JSON if needed.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.json_parser import JSONParser


def main():
    """Main function to run JSONParser"""
    try:
        # Get assets directory from command line or use default
        assets_dir = "assets"
        if len(sys.argv) > 1:
            assets_dir = sys.argv[1]
        
        # Check if assets directory exists
        if not Path(assets_dir).exists():
            print(f"❌ Assets directory not found: {assets_dir}")
            print(f"💡 Usage: python {sys.argv[0]} [assets_directory]")
            return 1
        
        # Initialize parser with verbose output
        print(f"🔍 Initializing JSONParser...")
        parser = JSONParser(
            assets_dir=assets_dir,
            quiet_warnings=False,
            more_data_show=True
        )
        
        # Load all sprite packs
        print(f"🚀 Loading sprite packs from: {assets_dir}")
        sprite_packs = parser.load_all_sprite_packs()
        
        # Print summary
        parser.print_summary()
        
        # Show detailed results
        print(f"\n📊 Detailed Results:")
        print(f"{'='*50}")
        
        for sprite_name, status in sprite_packs.items():
            status_icon = {
                "READY": "✅",
                "PARTIAL": "⚠️ ",
                "BROKEN": "❌"
            }.get(status, "❓")
            
            print(f"{status_icon} {sprite_name}: {status}")
            
            if sprite_name in parser.sprite_data:
                data = parser.sprite_data[sprite_name]
                if data.actions:
                    print(f"   📋 Actions: {len(data.actions)}")
                if data.behaviors:
                    print(f"   🎯 Behaviors: {len(data.behaviors)}")
                if data.errors:
                    print(f"   ❌ Errors: {len(data.errors)}")
                if data.warnings:
                    print(f"   ⚠️  Warnings: {len(data.warnings)}")
        
        # Test API functionality
        if sprite_packs:
            ready_sprites = parser.get_ready_sprite_names()
            if ready_sprites:
                test_sprite = ready_sprites[0]
                print(f"\n🧪 Testing API with '{test_sprite}':")
                
                actions = parser.get_actions(test_sprite)
                behaviors = parser.get_behaviors(test_sprite)
                
                print(f"   📋 Available actions: {list(actions.keys())}")
                print(f"   🎯 Available behaviors: {list(behaviors.keys())}")
                
                # Test condition evaluation
                if actions:
                    first_action = list(actions.keys())[0]
                    sprite_state = {"y": 100, "on_floor": True}
                    frames = parser.get_animation_for_condition(test_sprite, first_action, sprite_state)
                    
                    if frames:
                        print(f"   🎬 Animation frames for '{first_action}': {len(frames)}")
                    else:
                        print(f"   ⚠️  No animation frames found for '{first_action}'")
        
        print(f"\n✅ JSONParser execution completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Execution interrupted by user")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"💡 Check that assets directory exists and contains valid sprite packs")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 