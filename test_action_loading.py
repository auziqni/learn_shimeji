#!/usr/bin/env python3
"""
Test Action Loading
==================

Test untuk melihat bagaimana actions di-load
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.json_parser import JSONParser

def test_action_loading():
    """Test action loading"""
    print("🔍 Testing Action Loading...")
    
    # Initialize JSON parser
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=False, more_data_show=True)
    
    # Load all sprite packs
    results = json_parser.load_all_sprite_packs()
    print(f"📦 Load results: {results}")
    
    # Test Hornet specifically
    sprite_name = "Hornet"
    
    # Get all actions
    all_actions = json_parser.get_actions(sprite_name)
    print(f"\n📋 All actions for {sprite_name}:")
    for action_name, action_data in all_actions.items():
        print(f"  - {action_name} (type: {action_data.action_type})")
    
    # Get actions by type
    for action_type in ["Stay", "Move", "Animate", "Embedded"]:
        actions = json_parser.get_actions_by_type(sprite_name, action_type)
        print(f"\n🎯 {action_type} actions:")
        for action_name, action_data in actions.items():
            print(f"  - {action_name}")
            print(f"    Animation blocks: {len(action_data.animation_blocks)}")
            for i, block in enumerate(action_data.animation_blocks):
                print(f"      Block {i}: {len(block.frames)} frames")
                if block.condition:
                    print(f"        Condition: {block.condition}")
    
    # Test specific action
    stand_action = json_parser.get_action(sprite_name, "Stand")
    if stand_action:
        print(f"\n🎭 Stand action details:")
        print(f"  Type: {stand_action.action_type}")
        print(f"  Border: {stand_action.border_type}")
        print(f"  Animation blocks: {len(stand_action.animation_blocks)}")
        for i, block in enumerate(stand_action.animation_blocks):
            print(f"    Block {i}: {len(block.frames)} frames")
            for j, frame in enumerate(block.frames):
                print(f"      Frame {j}: {frame.image} (duration: {frame.duration})")
                if frame.image_anchor:
                    print(f"        Anchor: {frame.image_anchor}")

if __name__ == "__main__":
    test_action_loading() 