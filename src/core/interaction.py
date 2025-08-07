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
        
        # Update direction based on horizontal movement
        if dx != 0:
            pet.update_direction_from_movement(dx)
        
        # Update position state after movement
        from ..core.environment import Environment
        # Get environment from app_state if available
        # For now, we'll update position state in main.py where environment is available
    
    def handle_keyboard_events(self, event, app_state):
        """Handle all keyboard events and return True if event was handled"""
        if event.type != pygame.KEYDOWN:
            return False
        
        # System controls - ALWAYS ACTIVE
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
        
        # Check if debug mode is OFF - only allow system controls
        if not app_state['debug_manager'].debug_mode:
            return False  # Block all other keys when debug mode is OFF
        
        # Check if control panel is visible - only allow system controls
        if app_state['control_panel'].visible:
            return False  # Block all other keys when control panel is open
        
        # All other controls - only active when debug mode ON and control panel CLOSED
        return self._handle_debug_mode_controls(event, app_state)
    
    def _handle_debug_mode_controls(self, event, app_state):
        """Handle controls that are only active in debug mode with closed control panel"""
        
        # Pet selection controls
        if event.key == pygame.K_q:
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
    
    def update_pet_movement(self, pet_manager, environment, control_panel_visible, debug_mode):
        """Update pet movement based on current input"""
        # Block movement when control panel is open OR debug mode is off
        if control_panel_visible or not debug_mode:
            return
        
        keys = pygame.key.get_pressed()
        dx, dy = self.get_movement_from_input(keys)
        
        if dx != 0 or dy != 0:
            selected = pet_manager.get_selected_pet()
            if selected:
                self.apply_movement(selected, dx, dy)
                if environment:
                    environment.clamp_position(selected)
    
    # ===== THROWN DETECTION METHODS =====
    
    def detect_throw_gesture(self, pet, start_pos, end_pos, drag_time):
        """Detect if user gesture qualifies as throw"""
        import math
        
        # Calculate distance and velocity
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate velocity magnitude
        if drag_time > 0:
            velocity_magnitude = distance / drag_time
        else:
            velocity_magnitude = distance * 2.0  # Fallback for instant release
        
        # Check if velocity meets minimum threshold for throw
        min_throw_velocity = 50.0  # Minimum velocity to qualify as throw
        is_throw = velocity_magnitude >= min_throw_velocity
        
        # Log debug info
        from ..utils.log_manager import get_logger
        logger = get_logger("interaction")
        logger.debug(f"Throw detection - Distance: {distance:.1f}, Time: {drag_time:.3f}s, Velocity: {velocity_magnitude:.1f}, Is throw: {is_throw}")
        
        return is_throw
    
    def initiate_throw(self, pet, velocity_x, velocity_y):
        """Initiate thrown state with given velocity"""
        if pet and not pet.is_thrown:
            pet.start_thrown_state(velocity_x, velocity_y)
            return True
        return False
    
    def handle_thrown_input(self, pet, event):
        """Handle input events for thrown pets"""
        if not pet or not pet.is_thrown:
            return False
        
        # Block most input during thrown state
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Allow double-right-click to kill even during thrown state
            if event.button == 3:  # Right click
                return False  # Let main.py handle double-right-click detection
            else:
                return True  # Block other mouse input
        
        return False  # Block all other input during thrown state
    
    def handle_mouse_drag_for_throw(self, pet, mouse_pos, mouse_buttons):
        """Handle mouse drag for throw detection"""
        if not pet:
            return False
        
        # Start drag tracking on left mouse button down
        if mouse_buttons[0]:  # Left mouse button
            if not pet.is_dragging:
                pet.start_drag(mouse_pos[0], mouse_pos[1])
                pet.start_drag_tracking(mouse_pos[0], mouse_pos[1])
                from ..utils.log_manager import get_logger
                logger = get_logger("interaction")
                logger.debug(f"Started drag at ({mouse_pos[0]}, {mouse_pos[1]})")
                return True
            else:
                # Handle drag movement while button is pressed
                pet.update_drag(mouse_pos[0], mouse_pos[1])
                return True
        
        # Handle drag release and throw detection
        elif pet.is_dragging and not mouse_buttons[0]:
            # Calculate throw velocity
            drag_duration = pet.get_drag_duration()
            start_pos = pet.drag_start_pos
            end_pos = [mouse_pos[0], mouse_pos[1]]
            
            from ..utils.log_manager import get_logger
            logger = get_logger("interaction")
            logger.debug(f"Drag ended - Duration: {drag_duration:.3f}s, Start: {start_pos}, End: {end_pos}")
            
            # Check if gesture qualifies as throw
            if self.detect_throw_gesture(pet, start_pos, end_pos, drag_duration):
                # Calculate velocity using environment physics
                from ..core.environment import Environment
                # This will be called from main.py where environment is available
                logger.debug("THROW_DETECTED")
                return "THROW_DETECTED"
            
            # Normal drag end
            pet.stop_drag()
            logger.debug("DRAG_ENDED")
            return "DRAG_ENDED"
        
        return False 