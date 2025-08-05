# Sprite Name and Chat System for Desktop Pet Application
# This module handles name display and chat bubble rendering for sprites

import pygame
import config
from utils.log_manager import get_logger

class SpriteNameChat:
    """Name and chat bubble rendering system for desktop pets"""
    
    def __init__(self):
        self.logger = get_logger("sprite_name_chat")
        
        # Font initialization
        self.name_font = None
        self.chat_font = None
        self._initialize_fonts()
        
        # Colors
        self.name_color = (0, 100, 255)  # Blue
        self.chat_text_color = (0, 0, 0)  # Black
        self.chat_bg_color = (255, 255, 255)  # White
        
        # Chat bubble settings
        self.chat_padding = 8
        self.chat_radius = 6
        self.chat_max_width = 200
        self.chat_max_lines = 3
        self.chat_chars_per_line = 40
        
        self.logger.info("SpriteNameChat initialized")
    
    def _initialize_fonts(self):
        """Initialize fonts for name and chat"""
        try:
            # Initialize pygame.font if not already done
            if not pygame.font.get_init():
                pygame.font.init()
            
            # Name font - smaller, clean
            self.name_font = pygame.font.Font(None, 20)
            
            # Chat font - readable
            self.chat_font = pygame.font.Font(None, 16)
            
            self.logger.debug("Fonts initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize fonts: {e}")
            # Fallback to default font
            try:
                self.name_font = pygame.font.Font(None, 20)
                self.chat_font = pygame.font.Font(None, 16)
            except:
                self.logger.error("Could not initialize any fonts")
                self.name_font = None
                self.chat_font = None
    
    def render_name(self, surface, name: str, position: tuple, max_length: int = 25):
        """Render pet name below sprite"""
        if not name or len(name) == 0 or not self.name_font:
            return
        
        # Truncate name if too long
        display_name = name[:max_length]
        
        try:
            # Render name text
            name_surface = self.name_font.render(display_name, True, self.name_color)
            
            # Calculate position (center below sprite)
            name_rect = name_surface.get_rect()
            name_rect.centerx = position[0]
            name_rect.top = position[1] + 5  # 5 pixels below sprite
            
            # Draw name
            surface.blit(name_surface, name_rect)
            
        except Exception as e:
            self.logger.error(f"Failed to render name '{name}': {e}")
    
    def wrap_text(self, text: str, max_chars_per_line: int = 40, max_lines: int = 3) -> list:
        """Wrap text into lines"""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Check if adding this word would exceed line limit
            test_line = current_line + " " + word if current_line else word
            
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                # Current line is full, start new line
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, split it
                    lines.append(word[:max_chars_per_line])
                    current_line = word[max_chars_per_line:]
                
                # Check if we've reached max lines
                if len(lines) >= max_lines:
                    break
        
        # Add remaining line
        if current_line and len(lines) < max_lines:
            lines.append(current_line)
        
        return lines
    
    def render_chat_bubble(self, surface, chat_text: str, position: tuple):
        """Render chat bubble with wrapped text"""
        if not chat_text or len(chat_text) == 0 or not self.chat_font:
            return
        
        try:
            # Wrap text
            lines = self.wrap_text(chat_text, self.chat_chars_per_line, self.chat_max_lines)
            
            if not lines:
                return
            
            # Calculate text dimensions
            line_surfaces = []
            max_width = 0
            total_height = 0
            
            for line in lines:
                line_surface = self.chat_font.render(line, True, self.chat_text_color)
                line_surfaces.append(line_surface)
                max_width = max(max_width, line_surface.get_width())
                total_height += line_surface.get_height()
            
            # Add padding
            bubble_width = max_width + (self.chat_padding * 2)
            bubble_height = total_height + (self.chat_padding * 2)
            
            # Create bubble surface
            bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
            
            # Draw rounded rectangle background
            rect = pygame.Rect(0, 0, bubble_width, bubble_height)
            pygame.draw.rect(bubble_surface, self.chat_bg_color, rect, border_radius=self.chat_radius)
            
            # Draw text lines
            y_offset = self.chat_padding
            for line_surface in line_surfaces:
                bubble_surface.blit(line_surface, (self.chat_padding, y_offset))
                y_offset += line_surface.get_height()
            
            # Position bubble (top-right of sprite)
            bubble_rect = bubble_surface.get_rect()
            bubble_rect.bottomleft = (position[0] + 10, position[1] - 10)  # 10px offset from sprite
            
            # Draw bubble
            surface.blit(bubble_surface, bubble_rect)
            
        except Exception as e:
            self.logger.error(f"Failed to render chat bubble: {e}")
    
    def render_pet_text(self, surface, pet, name: str, chat: str):
        """Render both name and chat for a pet"""
        if not pet:
            return
        
        # Get pet position and size
        pet_x, pet_y = pet.get_position()
        pet_width = pet.width
        pet_height = pet.height
        
        # Calculate positions
        name_position = (pet_x + pet_width // 2, pet_y + pet_height)  # Center below sprite
        chat_position = (pet_x + pet_width, pet_y)  # Top-right of sprite
        
        # Render name
        self.render_name(surface, name, name_position)
        
        # Render chat bubble
        self.render_chat_bubble(surface, chat, chat_position) 