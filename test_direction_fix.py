#!/usr/bin/env python3
"""
Test Direction Fix
=================

Test sederhana untuk menguji perbaikan direction
"""

import sys
import os
import pygame

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.json_parser import JSONParser
from src.animation.animation_manager import AnimationManager
from src.animation.sprite_loader import SpriteLoader
from src.core.pet import Pet

def test_direction_fix():
    """Test direction fix"""
    print("🎯 Testing Direction Fix...")
    
    # Initialize pygame FIRST
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Initialize components
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True, more_data_show=False)
    sprite_loader = SpriteLoader()
    
    # Create pet
    pet = Pet(x=400, y=300, sprite_name="Hornet", json_parser=json_parser, action_type="Stay")
    pet.set_action("Stand")
    
    print(f"Initial direction: {pet.get_direction()}")
    print(f"Available actions: {pet.get_available_actions()}")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pet.set_direction("left")
                    print(f"Direction changed to: {pet.get_direction()}")
                elif event.key == pygame.K_RIGHT:
                    pet.set_direction("right")
                    print(f"Direction changed to: {pet.get_direction()}")
                elif event.key == pygame.K_SPACE:
                    # Move pet to test positioning
                    pet.x += 50
                    print(f"Pet moved to ({pet.x}, {pet.y})")
        
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
        pygame.draw.circle(screen, (255, 0, 0), (pet.x, pet.y), 5)
        
        # Draw frame rectangle (green)
        draw_x, draw_y = anchor_info['draw_position']
        frame_w, frame_h = anchor_info['frame_size']
        pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, frame_w, frame_h), 2)
        
        # Draw direction indicator (blue arrow)
        if pet.get_direction() == "right":
            # Draw arrow pointing right
            arrow_points = [(pet.x + 20, pet.y), (pet.x + 30, pet.y), (pet.x + 25, pet.y - 5)]
        else:
            # Draw arrow pointing left
            arrow_points = [(pet.x - 20, pet.y), (pet.x - 30, pet.y), (pet.x - 25, pet.y - 5)]
        pygame.draw.polygon(screen, (0, 0, 255), arrow_points)
        
        # Draw debug text
        debug_text = [
            f"Direction: {pet.get_direction()}",
            f"Base Pos: ({pet.x}, {pet.y})",
            f"Draw Pos: ({draw_x}, {draw_y})",
            f"Frame Size: {frame_w}x{frame_h}",
            f"Anchor: {anchor_info['anchor']}",
            "",
            "Controls:",
            "LEFT/RIGHT - Change direction",
            "SPACE - Move pet",
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
    print("✅ Direction fix test completed!")

if __name__ == "__main__":
    test_direction_fix() 