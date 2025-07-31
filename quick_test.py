#!/usr/bin/env python3
"""
Quick test untuk memverifikasi XML parser dengan namespace handling
"""

import sys
import os
sys.path.append('src')

from utils.xml_parser import XMLParser

def quick_test():
    print("🧪 Quick Test - XML Parser with Namespace Support")
    
    # Test dengan JSON debug enabled
    parser = XMLParser(save2json=True)
    
    # Load semua sprite packs
    sprite_packs = parser.load_all_sprite_packs()
    
    # Print summary
    parser.print_summary()
    
    # Test untuk Hornet sprite
    if "Hornet" in parser.get_all_sprite_names():
        print(f"\n🔍 Testing Hornet sprite:")
        
        # Get actions
        actions = parser.get_actions("Hornet")
        print(f"  Actions found: {len(actions)}")
        
        # Test beberapa actions
        for action_name in ["Stand", "Walk", "ClimbWall"]:
            if action_name in actions:
                action = actions[action_name]
                print(f"  📋 {action_name}: {len(action.animation_blocks)} animation blocks")
                
                if action.default_animation:
                    print(f"    Default: {len(action.default_animation.frames)} frames")
                
                for i, block in enumerate(action.animation_blocks):
                    print(f"    Block {i+1}: {len(block.frames)} frames")
                    if block.condition:
                        print(f"      Condition: {block.condition}")
        
        # Get behaviors
        behaviors = parser.get_behaviors("Hornet")
        print(f"  Behaviors found: {len(behaviors)}")
        
        # Test conditional behaviors
        conditional_behaviors = [b for b in behaviors.values() if b.condition]
        print(f"  Conditional behaviors: {len(conditional_behaviors)}")
        
        for behavior_name, behavior in list(behaviors.items())[:5]:  # Show first 5
            if behavior.condition:
                print(f"    🎯 {behavior_name}: {behavior.condition}")
    
    print("\n✅ Quick test completed!")

if __name__ == "__main__":
    quick_test() 