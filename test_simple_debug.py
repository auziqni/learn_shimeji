#!/usr/bin/env python3
"""
Simple Debug Test
================

Test sederhana untuk debug masalah loading
"""

import sys
import os
import pygame

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.json_parser import JSONParser
from src.animation.animation_manager import AnimationManager
from src.animation.sprite_loader import SpriteLoader

def test_simple_debug():
    """Simple debug test"""
    print("🔍 Simple Debug Test...")
    
    # Initialize pygame FIRST
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Initialize components
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=False, more_data_show=False)
    sprite_loader = SpriteLoader()
    
    # Load all sprite packs
    results = json_parser.load_all_sprite_packs()
    print(f"📦 Load results: {results}")
    
    # Test Hornet specifically
    sprite_name = "Hornet"
    action_type = "Stay"
    
    # Get actions by type
    actions = json_parser.get_actions_by_type(sprite_name, action_type)
    print(f"\n🎯 {action_type} actions for {sprite_name}: {len(actions)}")
    for action_name in actions.keys():
        print(f"  - {action_name}")
    
    # Test AnimationManager
    print(f"\n🎭 Testing AnimationManager...")
    anim_manager = AnimationManager(sprite_name, action_type, sprite_loader)
    
    # Load sprite data
    success = anim_manager.load_sprite_data(json_parser)
    print(f"Load success: {success}")
    print(f"Actions loaded: {len(anim_manager.actions)}")
    print(f"Action list: {anim_manager.action_list}")
    
    if anim_manager.action_list:
        # Test setting action
        first_action = anim_manager.action_list[0]
        print(f"Setting action: {first_action}")
        anim_manager.set_action(first_action)
        print(f"Current action: {anim_manager.get_current_action()}")
        print(f"Current image: {anim_manager.get_current_image() is not None}")
        
        # Test anchor info
        anchor = anim_manager.get_current_anchor()
        print(f"Current anchor: {anchor}")
        
        # Test draw position
        draw_pos = anim_manager.get_draw_position(400, 300)
        print(f"Draw position for (400, 300): {draw_pos}")
        
        # Test frame size
        frame_size = anim_manager.get_frame_size()
        print(f"Frame size: {frame_size}")

if __name__ == "__main__":
    test_simple_debug() 