#!/usr/bin/env python3
"""
Test Anchor-Based Positioning
============================

Test untuk menguji sistem anchor-based positioning
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
from src.core.pet import Pet

def test_anchor_positioning():
    """Test anchor-based positioning system"""
    print("🎯 Testing Anchor-Based Positioning...")
    
    # Initialize pygame FIRST
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Initialize components AFTER pygame display
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True, more_data_show=False)
    sprite_loader = SpriteLoader()
    
    # Create pet AFTER pygame display is initialized
    pet = Pet(x=400, y=300, sprite_name="Hornet", json_parser=json_parser, action_type="Stay")
    
    # Test different actions to see anchor positioning
    actions_to_test = ["Stand", "Sit", "BePet"]
    current_action_index = 0
    
    # Set initial action
    pet.set_action("Stand")
    print(f"Initial action: {pet.get_current_action()}")
    
    # Debug: Print available actions
    available_actions = pet.get_available_actions()
    print(f"Available actions: {available_actions}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Switch to next action
                    current_action_index = (current_action_index + 1) % len(actions_to_test)
                    pet.set_action(actions_to_test[current_action_index])
                    print(f"Switched to action: {actions_to_test[current_action_index]}")
                elif event.key == pygame.K_LEFT:
                    pet.x -= 10
                    print(f"Pet moved left to ({pet.x}, {pet.y})")
                elif event.key == pygame.K_RIGHT:
                    pet.x += 10
                    print(f"Pet moved right to ({pet.x}, {pet.y})")
                elif event.key == pygame.K_UP:
                    pet.y -= 10
                    print(f"Pet moved up to ({pet.x}, {pet.y})")
                elif event.key == pygame.K_DOWN:
                    pet.y += 10
                    print(f"Pet moved down to ({pet.x}, {pet.y})")
        
        # Update animation
        delta_time = clock.tick(60) / 1000.0
        pet.update_animation(delta_time)
        
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Draw pet
        pet.draw(screen)
        
        # Draw debug info
        anchor_info = pet.get_anchor_info()
        font = pygame.font.Font(None, 24)
        
        # Draw anchor point (red circle)
        if anchor_info['anchor']:
            pygame.draw.circle(screen, (255, 0, 0), (pet.x, pet.y), 5)
        
        # Draw frame rectangle (green)
        draw_x, draw_y = anchor_info['draw_position']
        frame_w, frame_h = anchor_info['frame_size']
        pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, frame_w, frame_h), 2)
        
        # Draw debug text
        debug_text = [
            f"Action: {pet.get_current_action()}",
            f"Base Pos: ({pet.x}, {pet.y})",
            f"Draw Pos: ({draw_x}, {draw_y})",
            f"Frame Size: {frame_w}x{frame_h}",
            f"Anchor: {anchor_info['anchor']}",
            f"Direction: {pet.get_direction()}",
            "",
            "Controls:",
            "SPACE - Switch action",
            "Arrow keys - Move pet",
            "Q - Quit"
        ]
        
        y_offset = 10
        for text in debug_text:
            if text:
                text_surface = font.render(text, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    pygame.quit()
    print("✅ Anchor positioning test completed!")

if __name__ == "__main__":
    test_anchor_positioning() 