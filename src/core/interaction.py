import pygame
from .pet import Pet

class Interaction:
    """Handles all input events, movement, and pet controls"""
    
    def __init__(self, speed=5.0):
        self.speed = speed
    
    def get_movement_from_input(self, keys):
        """Calculate movement vector from keyboard input (WASD only)"""
        dx, dy = 0, 0
        
        if keys[pygame.K_a]:
            dx = -self.speed
        elif keys[pygame.K_d]:
            dx = self.speed
        
        if keys[pygame.K_w]:
            dy = -self.speed
        elif keys[pygame.K_s]:
            dy = self.speed
        
        return (dx, dy)
    
    def apply_movement(self, pet, dx, dy):
        """Apply movement to pet"""
        current_x, current_y = pet.get_position()
        new_x = current_x + dx
        new_y = current_y + dy
        pet.set_position(new_x, new_y)
    
    def handle_keyboard_events(self, event, app_state):
        """Handle all keyboard events and return True if event was handled"""
        if event.type != pygame.KEYDOWN:
            return False
        
        # System controls
        if event.key == pygame.K_ESCAPE:
            app_state['running'] = False
            return True
        
        elif event.key == pygame.K_F1:
            app_state['debug_manager'].toggle_debug_mode()
            return True
        
        elif event.key == pygame.K_F2:
            app_state['control_panel'].toggle_visibility()
            status = "shown" if app_state['control_panel'].visible else "hidden"
            app_state['logger'].user_action("toggle_control_panel", f"Control panel {status}")
            print(f"🎛️ Control panel {status}")
            return True
        
        # Pet selection controls
        elif event.key == pygame.K_q:
            app_state['pet_manager'].select_previous()
            pet_num = app_state['pet_manager'].selected_index + 1
            app_state['logger'].user_action("select_pet", f"Selected pet #{pet_num}")
            print(f"Selected pet #{pet_num}")
            return True
        
        elif event.key == pygame.K_e:
            app_state['pet_manager'].select_next()
            pet_num = app_state['pet_manager'].selected_index + 1
            app_state['logger'].user_action("select_pet", f"Selected pet #{pet_num}")
            print(f"Selected pet #{pet_num}")
            return True
        
        # Pet management controls
        elif event.key == pygame.K_SPACE:
            self._add_new_pet(app_state)
            return True
        
        elif event.key == pygame.K_DELETE or event.key == pygame.K_x:
            self._remove_selected_pet(app_state)
            return True
        
        # Pet controls (only if pet exists)
        return self._handle_pet_controls(event, app_state)
    
    def _handle_pet_controls(self, event, app_state):
        """Handle pet-specific controls"""
        selected_pet = app_state['pet_manager'].get_selected_pet()
        if not selected_pet:
            return False
        
        # Sprite pack controls
        if event.key == pygame.K_UP:
            if selected_pet.next_sprite_pack():
                app_state['logger'].user_action("next_sprite_pack", f"Changed to: {selected_pet.get_current_sprite_pack()}")
                print(f"🔄 Next sprite pack: {selected_pet.get_current_sprite_pack()}")
            return True
        
        elif event.key == pygame.K_DOWN:
            if selected_pet.previous_sprite_pack():
                app_state['logger'].user_action("previous_sprite_pack", f"Changed to: {selected_pet.get_current_sprite_pack()}")
                print(f"🔄 Previous sprite pack: {selected_pet.get_current_sprite_pack()}")
            return True
        
        # Action type controls
        elif event.key == pygame.K_LEFT:
            if selected_pet.previous_action_type():
                app_state['logger'].user_action("previous_action_type", f"Changed to: {selected_pet.get_current_action_type()}")
                print(f"🔄 Previous action type: {selected_pet.get_current_action_type()}")
            return True
        
        elif event.key == pygame.K_RIGHT:
            if selected_pet.next_action_type():
                app_state['logger'].user_action("next_action_type", f"Changed to: {selected_pet.get_current_action_type()}")
                print(f"🔄 Next action type: {selected_pet.get_current_action_type()}")
            return True
        
        # Action controls
        elif event.key == pygame.K_z:
            if selected_pet.previous_action():
                app_state['logger'].user_action("previous_action", f"Changed to: {selected_pet.get_current_action_info()}")
                print(f"🔄 Previous action: {selected_pet.get_current_action_info()}")
            return True
        
        elif event.key == pygame.K_c:
            if selected_pet.next_action():
                app_state['logger'].user_action("next_action", f"Changed to: {selected_pet.get_current_action_info()}")
                print(f"🔄 Next action: {selected_pet.get_current_action_info()}")
            return True
        
        # Sound controls
        elif event.key == pygame.K_m:
            sound_status = selected_pet.toggle_sound()
            status = "ON" if sound_status else "OFF"
            app_state['logger'].user_action("toggle_sound", f"Sound {status}")
            print(f"🔊 Sound {status}")
            return True
        
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            current_volume = selected_pet.get_volume()
            new_volume = min(1.0, current_volume + 0.1)
            selected_pet.set_volume(new_volume)
            app_state['logger'].user_action("volume_up", f"Volume: {new_volume:.1f}")
            print(f"🔊 Volume: {new_volume:.1f}")
            return True
        
        elif event.key == pygame.K_MINUS:
            current_volume = selected_pet.get_volume()
            new_volume = max(0.0, current_volume - 0.1)
            selected_pet.set_volume(new_volume)
            app_state['logger'].user_action("volume_down", f"Volume: {new_volume:.1f}")
            print(f"🔊 Volume: {new_volume:.1f}")
            return True
        
        return False
    
    def _add_new_pet(self, app_state):
        """Add new pet to the scene"""
        try:
            # Create new pet with default position
            new_pet = Pet(100, 100, "Hornet", app_state['json_parser'])
            app_state['pet_manager'].add_pet(new_pet)
            pet_count = app_state['pet_manager'].get_pet_count()
            app_state['logger'].user_action("add_pet", f"Added pet #{pet_count}")
            print(f"➕ Added pet #{pet_count}")
        except Exception as e:
            app_state['logger'].error(f"Error adding pet: {e}")
            print(f"❌ Error adding pet: {e}")
    
    def _remove_selected_pet(self, app_state):
        """Remove selected pet from the scene"""
        if app_state['pet_manager'].get_pet_count() > 1:
            app_state['pet_manager'].remove_selected_pet()
            app_state['logger'].user_action("remove_pet", "Removed selected pet")
            print("➖ Removed selected pet")
        else:
            app_state['logger'].warning("Cannot remove last pet")
            print("⚠️ Cannot remove last pet")
    
    def update_pet_movement(self, pet_manager, environment, control_panel_visible):
        """Update pet movement based on current input"""
        if control_panel_visible:
            return
        
        keys = pygame.key.get_pressed()
        dx, dy = self.get_movement_from_input(keys)
        
        if dx != 0 or dy != 0:
            selected = pet_manager.get_selected_pet()
            if selected:
                self.apply_movement(selected, dx, dy)
                if environment:
                    environment.clamp_position(selected) 