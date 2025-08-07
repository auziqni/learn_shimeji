#!/usr/bin/env python3
"""
Test script for drag functionality
Tests mouse drag interaction with pets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.core.pet import Pet
from src.ui.pet_manager import PetManager
from src.core.environment import Environment
from src.utils.json_parser import JSONParser
from src.utils.settings_manager import SettingsManager

def test_drag_functionality():
    """Test drag functionality with simple pygame window"""
    print("🧪 Testing Drag Functionality")
    print("=" * 50)
    
    # Initialize pygame
    pygame.init()
    
    # Create test window
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Drag Functionality Test")
    
    # Initialize components
    settings_manager = SettingsManager()
    environment = Environment(screen_width, screen_height, settings_manager)
    pet_manager = PetManager()
    
    # Initialize JSON parser
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True)
    json_parser.load_all_sprite_packs()
    
    # Create test pets
    pet1 = Pet(100, 100, "Hornet", json_parser)
    pet2 = Pet(200, 150, "HiveKnight", json_parser)
    pet3 = Pet(300, 200, "HiveQueen", json_parser)
    
    pet_manager.add_pet(pet1)
    pet_manager.add_pet(pet2)
    pet_manager.add_pet(pet3)
    
    print(f"✅ Created {pet_manager.get_pet_count()} test pets")
    print(f"✅ Environment boundaries: {environment.boundaries}")
    
    # Test variables
    clock = pygame.time.Clock()
    running = True
    test_results = {
        'drag_started': False,
        'drag_updated': False,
        'drag_stopped': False,
        'boundary_respect': False,
        'pinched_state': False
    }
    
    print("\n🎮 Test Instructions:")
    print("1. Click and drag any pet with left mouse button")
    print("2. Try to drag outside boundaries (should be clamped)")
    print("3. Check debug info shows 'Pinched: True' during drag")
    print("4. Release mouse to stop dragging")
    print("5. Press ESC to exit test")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                # Handle mouse events through PetManager
                if pet_manager.handle_mouse_events(event, environment):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        test_results['drag_started'] = True
                        print("✅ Drag started successfully")
                    elif event.type == pygame.MOUSEBUTTONUP:
                        test_results['drag_stopped'] = True
                        print("✅ Drag stopped successfully")
                    elif event.type == pygame.MOUSEMOTION:
                        test_results['drag_updated'] = True
                        
                        # Check pinched state
                        dragged_pet = pet_manager.get_dragged_pet()
                        if dragged_pet and dragged_pet.is_pinched_state():
                            test_results['pinched_state'] = True
                        
                        # Check boundary respect
                        x, y = dragged_pet.get_position() if dragged_pet else (0, 0)
                        boundaries = environment.boundaries
                        if (boundaries['left_wall'] <= x <= boundaries['right_wall'] - dragged_pet.width and
                            boundaries['ceiling'] <= y <= boundaries['floor'] - dragged_pet.height):
                            test_results['boundary_respect'] = True
        
        # Update
        delta_time = clock.get_time() / 1000.0
        
        # Apply physics to non-dragged pets
        for pet in pet_manager.pets:
            if not pet.is_being_dragged():
                environment.apply_physics(pet, delta_time, False)
                pet.update_position_state(environment)
        
        # Render
        screen.fill((30, 30, 30))  # Dark gray background
        
        # Draw boundaries
        pygame.draw.line(screen, (0, 0, 255), 
                        (environment.boundaries['left_wall'], 0),
                        (environment.boundaries['left_wall'], screen_height), 3)
        pygame.draw.line(screen, (0, 0, 255),
                        (environment.boundaries['right_wall'], 0),
                        (environment.boundaries['right_wall'], screen_height), 3)
        pygame.draw.line(screen, (255, 255, 0),
                        (0, environment.boundaries['ceiling']),
                        (screen_width, environment.boundaries['ceiling']), 3)
        pygame.draw.line(screen, (0, 255, 0),
                        (0, environment.boundaries['floor']),
                        (screen_width, environment.boundaries['floor']), 3)
        
        # Draw pets
        pet_manager.draw_all(screen, debug_mode=True)
        
        # Draw selection indicator
        pet_manager.draw_selection_indicator(screen)
        
        # Draw test info
        font = pygame.font.Font(None, 24)
        info_lines = [
            "Drag Functionality Test",
            f"Pets: {pet_manager.get_pet_count()}",
            f"Dragging: {pet_manager.is_dragging()}",
            f"Selected: {pet_manager.selected_index + 1}",
            "",
            "Test Results:",
            f"Drag Started: {test_results['drag_started']}",
            f"Drag Updated: {test_results['drag_updated']}",
            f"Drag Stopped: {test_results['drag_stopped']}",
            f"Pinched State: {test_results['pinched_state']}",
            f"Boundary Respect: {test_results['boundary_respect']}",
            "",
            "Press ESC to exit"
        ]
        
        for i, line in enumerate(info_lines):
            color = (255, 255, 255) if i < 4 else (200, 200, 200)
            text_surface = font.render(line, True, color)
            screen.blit(text_surface, (10, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    
    # Print final test results
    print("\n📊 Test Results:")
    print("=" * 30)
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(test_results.values())
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    test_drag_functionality() 