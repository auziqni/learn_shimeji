import pygame
from ..utils.log_manager import get_logger
from ..animation.animation_manager import AnimationManager
from typing import Dict, Any, Tuple

class Pet:
    """Individual pet entity - handles image and position data with animation support and text display"""
    
    def __init__(self, x=0, y=0, sprite_name="Hornet", json_parser=None, name=None, chat=None, action_type="Stay"):
        self.logger = get_logger("pet")
        
        # Sprite pack management
        self.sprite_packs = ["Hornet", "HiveKnight", "HiveQueen"]
        self.current_sprite_pack_index = 0  # Default to "Hornet"
        
        # Action type management - Fixed action types
        self.action_types = ["Stay", "Move", "Animate", "Behavior", "Embedded"]
        self.current_action_type_index = 0  # Default to "Stay"
        
        # Store json_parser for action type cycling
        self.json_parser = json_parser
        
        # Initialize animation manager with action type filtering
        self.animation_manager = AnimationManager(sprite_name, action_type)
        
        # Load sprite data if json_parser is provided
        if json_parser:
            if not self.animation_manager.load_sprite_data(json_parser):
                self.logger.error(f"Failed to load sprite data for {sprite_name}")
                raise RuntimeError(f"Failed to load sprite data for {sprite_name}")
        
        # Position data
        self.x = x
        self.y = y
        
        # Direction tracking
        self.direction = "right"  # Default direction
        self.last_movement_direction = "right"  # Track last movement direction
        
        # Position state tracking
        self.onFloor = False
        self.onCeiling = False
        self.onLeftWall = False
        self.onRightWall = False
        self.closeToLeftWall = False
        self.closeToRightWall = False
        
        # Corner detection
        self.rightFloor = False
        self.leftFloor = False
        self.rightCeiling = False
        self.leftCeiling = False
        
        # Drag state management
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_pinched = False  # For debug info display
        
        # Text properties - use action info for chat
        self.name = sprite_name if name is None else name
        self.chat = self.animation_manager.get_current_action_info() if chat is None else chat
        
        # Get initial image from animation manager
        self.image = self.animation_manager.get_current_image()
        if self.image:
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        else:
            # Fallback if no image loaded
            default_sprite_size = (64, 64)  # Default fallback size
            fallback_color = (255, 0, 0)    # Default fallback color
            self.image = pygame.Surface(default_sprite_size)
            self.image.fill(fallback_color)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.logger.warning("Using fallback sprite - no image loaded from animation manager")
        
        self.logger.info(f"Pet created at position ({x}, {y}) with sprite '{sprite_name}', name '{self.name}', action_type '{action_type}'")
        self.logger.debug(f"Pet size: {self.width}x{self.height}")
    
    def get_rect(self):
        """Get pet's rectangle for collision detection and selection"""
        if not self.image:
            return pygame.Rect(self.x, self.y, 0, 0)
        
        # Use draw position for visual elements
        draw_x, draw_y = self.get_draw_position()
        return pygame.Rect(draw_x, draw_y, self.image.get_width(), self.image.get_height())
    
    def set_position(self, x, y):
        """Set pet position"""
        self.x = x
        self.y = y
    
    def get_position(self):
        """Get pet position"""
        return (self.x, self.y)
    
    def set_direction(self, direction):
        """Set pet direction (left/right)"""
        if direction in ["left", "right"]:
            self.direction = direction
            self.last_movement_direction = direction
            self.logger.debug(f"Pet direction changed to {direction}")
    
    def get_direction(self):
        """Get current pet direction"""
        return self.direction
    
    def get_last_movement_direction(self):
        """Get last movement direction"""
        return self.last_movement_direction
    
    def update_direction_from_movement(self, dx):
        """Update direction based on movement delta x"""
        if dx > 0:
            self.set_direction("right")
        elif dx < 0:
            self.set_direction("left")
    
    def start_drag(self, mouse_x, mouse_y):
        """Start dragging the pet"""
        if not self.is_dragging:
            self.is_dragging = True
            self.is_pinched = True
            
            # Calculate drag offset from mouse position to pet position
            draw_x, draw_y = self.get_draw_position()
            self.drag_offset_x = mouse_x - draw_x
            self.drag_offset_y = mouse_y - draw_y
            
            self.logger.debug(f"Started dragging pet at mouse ({mouse_x}, {mouse_y}) with offset ({self.drag_offset_x}, {self.drag_offset_y})")
    
    def update_drag(self, mouse_x, mouse_y, environment=None):
        """Update pet position during drag"""
        if not self.is_dragging:
            return
        
        # Calculate new position based on mouse and offset
        new_x = mouse_x - self.drag_offset_x
        new_y = mouse_y - self.drag_offset_y
        
        # Clamp to boundaries if environment is provided
        if environment:
            # Get boundaries
            boundaries = environment.boundaries
            
            # Clamp X position
            if new_x < boundaries['left_wall']:
                new_x = boundaries['left_wall']
            elif new_x + self.width > boundaries['right_wall']:
                new_x = boundaries['right_wall'] - self.width
            
            # Clamp Y position
            if new_y < boundaries['ceiling']:
                new_y = boundaries['ceiling']
            elif new_y + self.height > boundaries['floor']:
                new_y = boundaries['floor'] - self.height
        
        # Update position
        self.set_position(new_x, new_y)
        
        # Update position state
        if environment:
            self.update_position_state(environment)
    
    def stop_drag(self):
        """Stop dragging the pet"""
        if self.is_dragging:
            self.is_dragging = False
            self.is_pinched = False
            self.drag_offset_x = 0
            self.drag_offset_y = 0
            self.logger.debug("Stopped dragging pet")
    
    def is_being_dragged(self):
        """Check if pet is currently being dragged"""
        return self.is_dragging
    
    def is_pinched_state(self):
        """Get pinched state for debug info"""
        return self.is_pinched
    
    def update_position_state(self, environment):
        """Update position state based on current position and environment"""
        if not environment:
            return
        
        # Get virtual boundaries from environment
        boundaries = environment.boundaries
        
        # Calculate close to thresholds (20% of virtual boundary width)
        virtual_width = boundaries['right_wall'] - boundaries['left_wall']
        close_left_threshold = boundaries['left_wall'] + (virtual_width * 0.2)
        close_right_threshold = boundaries['right_wall'] - (virtual_width * 0.2)
        
        # Update position states using virtual boundaries
        self.onFloor = (self.y + self.height >= boundaries['floor'])
        self.onCeiling = (self.y <= boundaries['ceiling'])
        self.onLeftWall = (self.x <= boundaries['left_wall'])
        self.onRightWall = (self.x + self.width >= boundaries['right_wall'])
        self.closeToLeftWall = (self.x <= close_left_threshold)
        self.closeToRightWall = (self.x >= close_right_threshold)
        
        # Corner detection
        self.rightFloor = (self.y + self.height >= boundaries['floor']) and (self.x + self.width >= boundaries['right_wall'])
        self.leftFloor = (self.y + self.height >= boundaries['floor']) and (self.x <= boundaries['left_wall'])
        self.rightCeiling = (self.y <= boundaries['ceiling']) and (self.x + self.width >= boundaries['right_wall'])
        self.leftCeiling = (self.y <= boundaries['ceiling']) and (self.x <= boundaries['left_wall'])
    
    def get_position_state(self):
        """Get current position state as dictionary"""
        return {
            'onFloor': self.onFloor,
            'onCeiling': self.onCeiling,
            'onLeftWall': self.onLeftWall,
            'onRightWall': self.onRightWall,
            'closeToLeftWall': self.closeToLeftWall,
            'closeToRightWall': self.closeToRightWall,
            'rightFloor': self.rightFloor,
            'leftFloor': self.leftFloor,
            'rightCeiling': self.rightCeiling,
            'leftCeiling': self.leftCeiling
        }
    
    def get_position_state_text(self):
        """Get position state as compact text for debug display"""
        on_states = []
        close_states = []
        
        # Build on states
        if self.onFloor:
            on_states.append("F")
        if self.onCeiling:
            on_states.append("C")
        if self.onLeftWall:
            on_states.append("LW")
        if self.onRightWall:
            on_states.append("RW")
        
        # Build close states
        if self.closeToLeftWall:
            close_states.append("LW")
        if self.closeToRightWall:
            close_states.append("RW")
        
        # Format on states
        on_text = "/".join(on_states) if on_states else "n"
        
        # Format close states
        close_text = "/".join(close_states) if close_states else "n"
        
        return f"on:{on_text} , close:{close_text}"
    
    def set_name(self, name: str):
        """Set pet name"""
        if name and len(name) > 0:
            self.name = name[:25]  # Max 25 characters
            self.logger.debug(f"Pet name changed to '{self.name}'")
    
    def get_name(self) -> str:
        """Get pet name"""
        return self.name
    
    def set_chat(self, chat: str):
        """Set pet chat message"""
        self.chat = chat
        self.logger.debug(f"Pet chat changed to '{chat}'")
    
    def get_chat(self) -> str:
        """Get pet chat message"""
        return self.chat
    
    def get_flipped_image(self):
        """Get current image flipped based on direction"""
        if self.image:
            if self.direction == "right":
                flipped_image = pygame.transform.flip(self.image, True, False)
                return flipped_image.convert_alpha()
            else:
                return self.image
        return self.image
    
    def get_draw_position(self) -> Tuple[int, int]:
        """Get correct draw position with proper anchor point handling"""
        if not self.image:
            return (self.x, self.y)
        
        # Get current frame's anchor point
        anchor = self.animation_manager.get_current_anchor()
        if not anchor:
            # Default anchor at center bottom
            anchor = (self.image.get_width() // 2, self.image.get_height())
        
        # Calculate draw position based on anchor point
        draw_x = self.x - anchor[0]
        draw_y = self.y - anchor[1]
        
        # Adjust for direction
        if self.direction == "right":
            # When facing right, anchor should be at the left side of the sprite
            # So we need to adjust the draw position
            frame_width = self.image.get_width()
            draw_x = self.x - (frame_width - anchor[0])
        
        # for offset
        draw_x = draw_x + 64
        draw_y = draw_y + 128
        return (draw_x, draw_y)
    
    def get_frame_size(self) -> Tuple[int, int]:
        """Get current frame size"""
        return self.animation_manager.get_frame_size()
    
    def get_anchor_info(self) -> Dict[str, Any]:
        """Get anchor information for debugging"""
        anchor = self.animation_manager.get_current_anchor()
        frame_size = self.get_frame_size()
        draw_pos = self.get_draw_position()
        
        return {
            'anchor': anchor,
            'frame_size': frame_size,
            'draw_position': draw_pos,
            'base_position': (self.x, self.y)
        }
    
    def draw_arrow_indicator(self, surface, debug_mode=False):
        """Draw direction arrow indicator"""
        if not debug_mode:
            return
        
        # Arrow properties
        arrow_size = 8
        arrow_color = (255, 255, 0)  # Yellow
        
        # Use draw position for visual elements
        draw_x, draw_y = self.get_draw_position()
        frame_w, frame_h = self.get_frame_size()
        
        # Calculate arrow position relative to frame
        if self.direction == "right":
            # Arrow on right side pointing right
            arrow_x = draw_x + frame_w - arrow_size - 2
            arrow_y = draw_y + 2
            # Create right-pointing arrow
            arrow_points = [
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x + arrow_size, arrow_y + arrow_size//2),
                (arrow_x + arrow_size - 2, arrow_y),
                (arrow_x + arrow_size - 2, arrow_y + arrow_size)
            ]
        else:
            # Arrow on left side pointing left
            arrow_x = draw_x + 2
            arrow_y = draw_y + 2
            # Create left-pointing arrow
            arrow_points = [
                (arrow_x + arrow_size, arrow_y + arrow_size//2),
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x + 2, arrow_y),
                (arrow_x + 2, arrow_y + arrow_size)
            ]
        
        # Draw arrow
        try:
            pygame.draw.polygon(surface, arrow_color, arrow_points)
        except Exception as e:
            self.logger.debug(f"Failed to draw arrow: {e}")
    
    def draw_drag_indicator(self, surface, debug_mode=False):
        """Draw drag indicator when pet is being dragged"""
        if not debug_mode or not self.is_dragging:
            return
        
        # Draw drag indicator (red border around pet)
        draw_x, draw_y = self.get_draw_position()
        frame_w, frame_h = self.get_frame_size()
        
        # Red border for dragged pet
        drag_color = (255, 0, 0)  # Red
        border_thickness = 3
        pygame.draw.rect(surface, drag_color, (draw_x, draw_y, frame_w, frame_h), border_thickness)
        
        # Draw drag offset indicator
        offset_color = (255, 255, 0)  # Yellow
        pygame.draw.circle(surface, offset_color, (self.x, self.y), 5)  # Draw at anchor point
    
    def next_action_type(self):
        """Go to next action type"""
        self.current_action_type_index = (self.current_action_type_index + 1) % len(self.action_types)
        new_action_type = self.action_types[self.current_action_type_index]
        
        # Create new animation manager with new action type
        self.animation_manager = AnimationManager(self.animation_manager.sprite_name, new_action_type)
        
        # Reload sprite data with new action type
        if hasattr(self, 'json_parser') and self.json_parser:
            if self.animation_manager.load_sprite_data(self.json_parser):
                # Update image and chat
                new_image = self.animation_manager.get_current_image()
                if new_image:
                    self.image = new_image
                    self.width = self.image.get_width()
                    self.height = self.image.get_height()
                
                self.chat = self.animation_manager.get_current_action_info()
                self.logger.debug(f"Changed to next action type: {new_action_type}")
                return True
        
        return False
    
    def previous_action_type(self):
        """Go to previous action type"""
        self.current_action_type_index = (self.current_action_type_index - 1) % len(self.action_types)
        new_action_type = self.action_types[self.current_action_type_index]
        
        # Create new animation manager with new action type
        self.animation_manager = AnimationManager(self.animation_manager.sprite_name, new_action_type)
        
        # Reload sprite data with new action type
        if hasattr(self, 'json_parser') and self.json_parser:
            if self.animation_manager.load_sprite_data(self.json_parser):
                # Update image and chat
                new_image = self.animation_manager.get_current_image()
                if new_image:
                    self.image = new_image
                    self.width = self.image.get_width()
                    self.height = self.image.get_height()
                
                self.chat = self.animation_manager.get_current_action_info()
                self.logger.debug(f"Changed to previous action type: {new_action_type}")
                return True
        
        return False
    
    def get_current_action_type(self) -> str:
        """Get current action type"""
        return self.action_types[self.current_action_type_index]
    
    def next_action(self):
        """Go to next action"""
        if self.animation_manager.next_action():
            # Update image after action change
            new_image = self.animation_manager.get_current_image()
            if new_image:
                self.image = new_image
                self.width = self.image.get_width()
                self.height = self.image.get_height()
            
            # Update chat with new action info
            self.chat = self.animation_manager.get_current_action_info()
            self.logger.debug(f"Changed to next action: {self.chat}")
            return True
        return False
    
    def previous_action(self):
        """Go to previous action"""
        if self.animation_manager.previous_action():
            # Update image after action change
            new_image = self.animation_manager.get_current_image()
            if new_image:
                self.image = new_image
                self.width = self.image.get_width()
                self.height = self.image.get_height()
            
            # Update chat with new action info
            self.chat = self.animation_manager.get_current_action_info()
            self.logger.debug(f"Changed to previous action: {self.chat}")
            return True
        return False
    
    def set_action(self, action_name: str):
        """Set pet action"""
        if self.animation_manager.set_action(action_name):
            # Update image after action change
            new_image = self.animation_manager.get_current_image()
            if new_image:
                self.image = new_image
                self.width = self.image.get_width()
                self.height = self.image.get_height()
            
            # Update chat with new action info
            self.chat = self.animation_manager.get_current_action_info()
            self.logger.debug(f"Changed action to '{action_name}'")
            return True
        return False
    
    def get_current_action(self) -> str:
        """Get current action name"""
        return self.animation_manager.get_current_action()
    
    def get_current_action_info(self) -> str:
        """Get current action info in format '[actiontype] : [actionname]'"""
        return self.animation_manager.get_current_action_info()
    
    def get_available_actions(self) -> list:
        """Get list of available actions"""
        return self.animation_manager.get_available_actions()
    
    def update_animation(self, delta_time: float):
        """Update animation"""
        self.animation_manager.update_animation(delta_time)
        
        # Update image if animation changed
        new_image = self.animation_manager.get_current_image()
        if new_image and new_image != self.image:
            self.image = new_image
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            self.logger.debug(f"Pet image updated: {self.width}x{self.height}")
    
    def draw(self, surface):
        """Draw pet to surface"""
        # Use flipped image based on direction
        flipped_image = self.get_flipped_image()
        # Use anchor-based positioning
        draw_pos = self.get_draw_position()
        surface.blit(flipped_image, draw_pos)
    
    def next_sprite_pack(self):
        """Go to next sprite pack"""
        self.current_sprite_pack_index = (self.current_sprite_pack_index + 1) % len(self.sprite_packs)
        new_sprite_pack = self.sprite_packs[self.current_sprite_pack_index]
        
        # Create new animation manager with new sprite pack
        self.animation_manager = AnimationManager(new_sprite_pack, self.get_current_action_type())
        
        # Reload sprite data with new sprite pack
        if hasattr(self, 'json_parser') and self.json_parser:
            if self.animation_manager.load_sprite_data(self.json_parser):
                # Update image and chat
                new_image = self.animation_manager.get_current_image()
                if new_image:
                    self.image = new_image
                    self.width = self.image.get_width()
                    self.height = self.image.get_height()
                
                # Update name to new sprite pack
                self.name = new_sprite_pack
                
                self.chat = self.animation_manager.get_current_action_info()
                self.logger.debug(f"Changed to next sprite pack: {new_sprite_pack}")
                return True
        
        return False
    
    def previous_sprite_pack(self):
        """Go to previous sprite pack"""
        self.current_sprite_pack_index = (self.current_sprite_pack_index - 1) % len(self.sprite_packs)
        new_sprite_pack = self.sprite_packs[self.current_sprite_pack_index]
        
        # Create new animation manager with new sprite pack
        self.animation_manager = AnimationManager(new_sprite_pack, self.get_current_action_type())
        
        # Reload sprite data with new sprite pack
        if hasattr(self, 'json_parser') and self.json_parser:
            if self.animation_manager.load_sprite_data(self.json_parser):
                # Update image and chat
                new_image = self.animation_manager.get_current_image()
                if new_image:
                    self.image = new_image
                    self.width = self.image.get_width()
                    self.height = self.image.get_height()
                
                # Update name to new sprite pack
                self.name = new_sprite_pack
                
                self.chat = self.animation_manager.get_current_action_info()
                self.logger.debug(f"Changed to previous sprite pack: {new_sprite_pack}")
                return True
        
        return False
    
    def get_current_sprite_pack(self) -> str:
        """Get current sprite pack"""
        return self.sprite_packs[self.current_sprite_pack_index]
    
    def play_sound(self, sound_name: str):
        """Play a sound"""
        return self.animation_manager.play_sound(sound_name)
    
    def set_volume(self, volume: float):
        """Set volume for all sounds"""
        self.animation_manager.set_volume(volume)
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        return self.animation_manager.toggle_sound()
    
    def get_sound_status(self) -> bool:
        """Get current sound status"""
        return self.animation_manager.get_sound_status()
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.animation_manager.get_volume() 

    def get_animation_info(self) -> Dict[str, Any]:
        """Get animation information for debugging"""
        return self.animation_manager.get_animation_info() 