#!/usr/bin/env python3
"""
Test script to verify anchor-based positioning for chat bubbles and names
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.utils.json_parser import JSONParser
from src.core.pet import Pet
from src.ui.sprite_name_chat import SpriteNameChat

def test_anchor_positioning():
    """Test anchor-based positioning for chat bubbles and names"""
    
    print("🧪 Testing anchor-based positioning for chat bubbles and names...")
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Anchor Positioning Test")
    clock = pygame.time.Clock()
    
    # Initialize JSON parser
    json_parser = JSONParser()
    
    # Create test pet with "Stand" action (which is a "Stay" type action)
    pet = Pet(x=400, y=300, sprite_name="Hornet", json_parser=json_parser, action_type="Stay")
    pet.set_name("Test Pet")
    pet.set_chat("Hello! This is a test chat bubble positioned using anchor points.")
    
    # Create sprite name chat system
    sprite_name_chat = SpriteNameChat()
    
    # Test different positions
    test_positions = [
        (200, 200),
        (400, 300),
        (600, 400),
        (300, 500)
    ]
    
    current_position = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Change position
                    current_position = (current_position + 1) % len(test_positions)
                    new_x, new_y = test_positions[current_position]
                    pet.set_position(new_x, new_y)
                    print(f"📍 Moved pet to position ({new_x}, {new_y})")
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill((50, 50, 50))
        
        # Draw pet
        pet.draw(screen)
        
        # Draw name and chat using anchor-based positioning
        sprite_name_chat.render_pet_text(screen, pet, pet.get_name(), pet.get_chat())
        
        # Draw anchor point indicator
        anchor_info = pet.get_anchor_info()
        if anchor_info:
            anchor = anchor_info.get('anchor')
            if anchor:
                # Draw anchor point as red circle
                pygame.draw.circle(screen, (255, 0, 0), (pet.x, pet.y), 3)
                
                # Draw anchor info text
                font = pygame.font.Font(None, 24)
                info_text = f"Anchor: {anchor}"
                text_surface = font.render(info_text, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10))
        
        # Draw instructions
        font = pygame.font.Font(None, 20)
        instructions = [
            "SPACE: Change position",
            "ESC: Exit",
            "Red dot: Anchor point",
            "Blue text: Name (below sprite)",
            "White bubble: Chat (above-right of sprite)"
        ]
        
        for i, instruction in enumerate(instructions):
            text_surface = font.render(instruction, True, (200, 200, 200))
            screen.blit(text_surface, (10, 40 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ Anchor positioning test completed!")

if __name__ == "__main__":
    test_anchor_positioning() 