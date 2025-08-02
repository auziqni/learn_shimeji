# main.py - Simple Control Panel dengan 4 Tabs
# Updated to demonstrate animation.py integration with json_parser.py

from PyQt5.QtWidgets import QApplication
import sys
import pygame

from control_panel import ControlPanel
from utils.json_parser import JSONParser
from animation import AnimationManager


def main():
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Teknisee Shimeji TikTok")
    app.setApplicationVersion("0.1.0")
    
    # Initialize pygame for animation system
    pygame.init()
    
    # Initialize JSON parser
    json_parser = JSONParser(assets_dir="assets", quiet_warnings=True, more_data_show=True)
    
    # Load all sprite packs
    sprite_packs = json_parser.load_all_sprite_packs()
    json_parser.print_summary()
    
    # Initialize animation manager with JSON parser
    animation_manager = AnimationManager(json_parser)
    
    # Load animations for available sprites
    ready_sprites = json_parser.get_ready_sprite_names()
    print(f"\n🎬 Loading animations for {len(ready_sprites)} ready sprites...")
    
    for sprite_name in ready_sprites:
        success = animation_manager.load_sprite_animations(sprite_name)
        if success:
            actions = animation_manager.get_available_actions(sprite_name)
            print(f"  ✅ {sprite_name}: {len(actions)} actions loaded")
            if actions:
                print(f"     Available actions: {', '.join(actions[:5])}{'...' if len(actions) > 5 else ''}")
        else:
            print(f"  ❌ {sprite_name}: Failed to load animations")
    
    # Create dan show window
    window = ControlPanel()
    window.show()
    
    # Example: Start a test animation (uncomment to test)
    # if ready_sprites:
    #     test_sprite = ready_sprites[0]
    #     actions = animation_manager.get_available_actions(test_sprite)
    #     if actions:
    #         test_action = actions[0]
    #         print(f"\n🎭 Testing animation: {test_sprite} - {test_action}")
    #         animation_manager.start_animation("test_pet_1", test_sprite, test_action)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
