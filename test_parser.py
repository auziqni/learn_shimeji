#!/usr/bin/env python3
"""
Test file untuk memverifikasi XML parser yang sudah diupdate
"""

import sys
import os
sys.path.append('src')

from utils.xml_parser import XMLParser

def test_parser():
    print("🧪 Testing Smart XML Parser...")
    
    # Test dengan JSON debug enabled
    parser = XMLParser(save2json=True)
    
    # Load semua sprite packs
    sprite_packs = parser.load_all_sprite_packs()
    
    # Print summary
    parser.print_summary()
    
    # Test untuk setiap sprite pack
    for sprite_name in parser.get_all_sprite_names():
        print(f"\n🔍 Testing sprite: {sprite_name}")
        
        # Get actions
        actions = parser.get_actions(sprite_name)
        print(f"  Actions found: {len(actions)}")
        
        # Test setiap action
        for action_name, action in actions.items():
            print(f"  📋 Action: {action_name}")
            print(f"    Type: {action.action_type}")
            print(f"    Border: {action.border_type}")
            print(f"    Animation blocks: {len(action.animation_blocks)}")
            
            if action.default_animation:
                print(f"    Default frames: {len(action.default_animation.frames)}")
            
            # Test conditional animations
            for i, block in enumerate(action.animation_blocks):
                print(f"    Block {i+1}: {len(block.frames)} frames")
                if block.condition:
                    print(f"      Condition: {block.condition}")
        
        # Get behaviors
        behaviors = parser.get_behaviors(sprite_name)
        print(f"  Behaviors found: {len(behaviors)}")
        
        # Test conditional behaviors
        conditional_behaviors = [b for b in behaviors.values() if b.condition]
        print(f"  Conditional behaviors: {len(conditional_behaviors)}")
        
        for behavior_name, behavior in behaviors.items():
            if behavior.condition:
                print(f"    🎯 {behavior_name}: {behavior.condition}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_parser() 