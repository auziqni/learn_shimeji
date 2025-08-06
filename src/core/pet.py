import pygame
from ..utils.log_manager import get_logger
from ..animation.animation_manager import AnimationManager

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
        """Get pygame rect for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
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
                return pygame.transform.flip(self.image, True, False)
            else:
                return self.image
        return self.image
    
    def get_draw_position(self) -> tuple:
        """Get the correct drawing position - simple top-left positioning"""
        if not self.image:
            return (self.x, self.y)
        
        # Simple top-left positioning without anchor point
        return (self.x, self.y)
    
    def draw_arrow_indicator(self, surface, debug_mode=False):
        """Draw direction arrow indicator"""
        if not debug_mode:
            return
        
        # Arrow properties
        arrow_size = 8
        arrow_color = (255, 255, 0)  # Yellow
        
        # Calculate arrow position (top corner of sprite)
        if self.direction == "right":
            # Arrow on right side pointing right
            arrow_x = self.x + self.width - arrow_size - 2
            arrow_y = self.y + 2
            # Create right-pointing arrow
            arrow_points = [
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x + arrow_size, arrow_y + arrow_size//2),
                (arrow_x + arrow_size - 2, arrow_y),
                (arrow_x + arrow_size - 2, arrow_y + arrow_size)
            ]
        else:
            # Arrow on left side pointing left
            arrow_x = self.x + 2
            arrow_y = self.y + 2
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