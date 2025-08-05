# UI Components for Desktop Pet Application
# This module contains reusable UI components with functional implementations

import pygame
import config
from typing import Optional, Callable, Tuple, Dict, Any
from utils.log_manager import get_logger

class UIComponent:
    """Base class for UI components with common functionality"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self.rect = pygame.Rect(x, y, width, height)
        
        # State management
        self.hovered = False
        self.focused = False
        self.pressed = False
        
        # Styling
        self.style = {
            'background_color': (100, 100, 100),
            'border_color': (150, 150, 150),
            'text_color': (255, 255, 255),
            'hover_color': (120, 120, 120),
            'pressed_color': (80, 80, 80),
            'disabled_color': (60, 60, 60),
            'border_width': 2,
            'corner_radius': 5
        }
        
        self.logger = get_logger("ui_component")
    
    def render(self, surface):
        """Base render method - should be overridden"""
        if not self.visible:
            return
        
        # Draw background
        color = self._get_background_color()
        pygame.draw.rect(surface, color, self.rect)
        
        # Draw border
        if self.style['border_width'] > 0:
            pygame.draw.rect(surface, self.style['border_color'], self.rect, self.style['border_width'])
    
    def handle_event(self, event) -> bool:
        """Base event handling - should be overridden"""
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        
        return False
    
    def _handle_mouse_motion(self, event) -> bool:
        """Handle mouse motion events"""
        old_hovered = self.hovered
        self.hovered = self.rect.collidepoint(event.pos)
        
        if old_hovered != self.hovered:
            self._on_hover_change(self.hovered)
            return True
        
        return False
    
    def _handle_mouse_down(self, event) -> bool:
        """Handle mouse button down events"""
        if self.rect.collidepoint(event.pos):
            self.pressed = True
            self.focused = True
            self._on_press()
            return True
        
        return False
    
    def _handle_mouse_up(self, event) -> bool:
        """Handle mouse button up events"""
        if self.pressed:
            self.pressed = False
            if self.rect.collidepoint(event.pos):
                self._on_click()
            self._on_release()
            return True
        
        return False
    
    def _get_background_color(self):
        """Get appropriate background color based on state"""
        if not self.enabled:
            return self.style['disabled_color']
        elif self.pressed:
            return self.style['pressed_color']
        elif self.hovered:
            return self.style['hover_color']
        else:
            return self.style['background_color']
    
    def _on_hover_change(self, hovered: bool):
        """Called when hover state changes"""
        pass
    
    def _on_press(self):
        """Called when component is pressed"""
        pass
    
    def _on_release(self):
        """Called when component is released"""
        pass
    
    def _on_click(self):
        """Called when component is clicked"""
        pass
    
    def update_hover_state(self, mouse_pos: Tuple[int, int]):
        """Update hover state based on mouse position"""
        old_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if old_hovered != self.hovered:
            self._on_hover_change(self.hovered)
    
    def set_position(self, x: int, y: int):
        """Set component position"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width: int, height: int):
        """Set component size"""
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height

class Button(UIComponent):
    """Functional button component with styling and callbacks"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, callback: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        
        # Button-specific styling
        self.style.update({
            'background_color': (70, 130, 180),  # Steel blue
            'hover_color': (100, 149, 237),      # Cornflower blue
            'pressed_color': (65, 105, 225),     # Royal blue
            'text_color': (255, 255, 255),
            'border_color': (255, 255, 255),
            'corner_radius': 8
        })
        
        self.logger = get_logger("button")
    
    def render(self, surface):
        """Render button with proper styling"""
        if not self.visible:
            return
        
        # Draw background with rounded corners
        color = self._get_background_color()
        pygame.draw.rect(surface, color, self.rect, border_radius=self.style['corner_radius'])
        
        # Draw border
        if self.style['border_width'] > 0:
            pygame.draw.rect(surface, self.style['border_color'], self.rect, 
                           self.style['border_width'], border_radius=self.style['corner_radius'])
        
        # Draw text
        self._render_text(surface)
    
    def _render_text(self, surface):
        """Render button text"""
        try:
            font = pygame.font.Font(None, 24)
            text_surface = font.render(self.text, True, self.style['text_color'])
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            self.logger.warning(f"Failed to render button text: {e}")
    
    def _on_click(self):
        """Handle button click"""
        if self.callback:
            try:
                self.callback()
                self.logger.debug(f"Button '{self.text}' clicked")
            except Exception as e:
                self.logger.error(f"Button callback error: {e}")

class Slider(UIComponent):
    """Functional slider component with value tracking"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_value: float, max_value: float, current_value: float,
                 on_change: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = current_value
        self.on_change = on_change
        self.dragging = False
        
        # Slider-specific styling
        self.style.update({
            'background_color': (50, 50, 50),    # Dark gray
            'slider_color': (100, 149, 237),     # Cornflower blue
            'hover_color': (60, 60, 60),
            'border_color': (150, 150, 150),
            'corner_radius': 10
        })
        
        self.logger = get_logger("slider")
    
    def render(self, surface):
        """Render slider with track and handle"""
        if not self.visible:
            return
        
        # Draw track
        track_color = self.style['background_color']
        pygame.draw.rect(surface, track_color, self.rect, border_radius=self.style['corner_radius'])
        
        # Draw border
        pygame.draw.rect(surface, self.style['border_color'], self.rect, 
                       1, border_radius=self.style['corner_radius'])
        
        # Draw handle
        self._render_handle(surface)
    
    def _render_handle(self, surface):
        """Render slider handle"""
        # Calculate handle position
        value_ratio = (self.current_value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.x + (self.width - 20) * value_ratio
        handle_rect = pygame.Rect(handle_x, self.y + 2, 20, self.height - 4)
        
        # Draw handle
        handle_color = self.style['slider_color'] if self.hovered or self.dragging else self.style['background_color']
        pygame.draw.rect(surface, handle_color, handle_rect, border_radius=8)
    
    def _handle_mouse_down(self, event) -> bool:
        """Handle mouse down for slider dragging"""
        if self.rect.collidepoint(event.pos):
            self.dragging = True
            self._update_value_from_mouse(event.pos[0])
            return True
        return False
    
    def _handle_mouse_motion(self, event) -> bool:
        """Handle mouse motion for slider dragging"""
        if self.dragging:
            self._update_value_from_mouse(event.pos[0])
            return True
        
        return super()._handle_mouse_motion(event)
    
    def _handle_mouse_up(self, event) -> bool:
        """Handle mouse up to stop dragging"""
        if self.dragging:
            self.dragging = False
            return True
        return super()._handle_mouse_up(event)
    
    def _update_value_from_mouse(self, mouse_x: int):
        """Update slider value based on mouse position"""
        # Calculate new value
        track_width = self.width - 20
        relative_x = max(0, min(mouse_x - self.x, track_width))
        ratio = relative_x / track_width
        new_value = self.min_value + ratio * (self.max_value - self.min_value)
        
        # Update value if changed
        if abs(new_value - self.current_value) > 0.01:
            self.current_value = new_value
            if self.on_change:
                self.on_change(self.current_value)
    
    def set_value(self, value: float):
        """Set slider value"""
        self.current_value = max(self.min_value, min(value, self.max_value))

class Panel(UIComponent):
    """Reusable panel component with tabs and content areas"""
    
    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        super().__init__(x, y, width, height)
        self.title = title
        self.tabs = []
        self.buttons = []
        self.active_tab = None
        
        # Panel-specific styling
        self.style.update({
            'background_color': (40, 40, 40),    # Dark gray
            'border_color': (100, 100, 100),
            'title_color': (255, 255, 255),
            'corner_radius': 5
        })
        
        self.logger = get_logger("panel")
    
    def render(self, surface):
        """Render panel with title and content"""
        if not self.visible:
            return
        
        # Draw panel background
        pygame.draw.rect(surface, self.style['background_color'], self.rect, 
                        border_radius=self.style['corner_radius'])
        
        # Draw border
        pygame.draw.rect(surface, self.style['border_color'], self.rect, 
                        self.style['border_width'], border_radius=self.style['corner_radius'])
        
        # Draw title
        if self.title:
            self._render_title(surface)
        
        # Draw tabs
        self._render_tabs(surface)
        
        # Draw buttons
        self._render_buttons(surface)
    
    def _render_title(self, surface):
        """Render panel title"""
        try:
            font = pygame.font.Font(None, 20)
            text_surface = font.render(self.title, True, self.style['title_color'])
            text_rect = text_surface.get_rect(x=self.x + 10, y=self.y + 5)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            self.logger.warning(f"Failed to render panel title: {e}")
    
    def _render_tabs(self, surface):
        """Render panel tabs"""
        tab_y = self.y + 30
        for i, tab in enumerate(self.tabs):
            tab_x = self.x + 10 + i * 80
            tab_rect = pygame.Rect(tab_x, tab_y, 70, 25)
            
            # Tab styling
            tab_color = self.style['slider_color'] if tab == self.active_tab else self.style['background_color']
            pygame.draw.rect(surface, tab_color, tab_rect, border_radius=3)
            
            # Tab text
            try:
                font = pygame.font.Font(None, 16)
                text_surface = font.render(tab, True, self.style['text_color'])
                text_rect = text_surface.get_rect(center=tab_rect.center)
                surface.blit(text_surface, text_rect)
            except Exception as e:
                self.logger.warning(f"Failed to render tab text: {e}")
    
    def _render_buttons(self, surface):
        """Render panel buttons"""
        for button in self.buttons:
            if hasattr(button, 'render'):
                button.render(surface)
    
    def add_tab(self, tab_name: str):
        """Add a new tab to the panel"""
        self.tabs.append(tab_name)
        if not self.active_tab:
            self.active_tab = tab_name
    
    def add_button(self, button: Button):
        """Add a button to the panel"""
        self.buttons.append(button)
    
    def set_active_tab(self, tab_name: str):
        """Set the active tab"""
        if tab_name in self.tabs:
            self.active_tab = tab_name

class TextBox(UIComponent):
    """Text input component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, placeholder: str = ""):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.cursor_pos = 0
        self.focused = False
        
        # TextBox-specific styling
        self.style.update({
            'background_color': (60, 60, 60),
            'text_color': (255, 255, 255),
            'placeholder_color': (150, 150, 150),
            'cursor_color': (255, 255, 255),
            'border_color': (100, 100, 100)
        })
        
        self.logger = get_logger("textbox")
    
    def render(self, surface):
        """Render text box with text and cursor"""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(surface, self.style['background_color'], self.rect)
        
        # Draw border
        border_color = self.style['slider_color'] if self.focused else self.style['border_color']
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Draw text
        self._render_text(surface)
        
        # Draw cursor if focused
        if self.focused:
            self._render_cursor(surface)
    
    def _render_text(self, surface):
        """Render text or placeholder"""
        try:
            font = pygame.font.Font(None, 20)
            display_text = self.text if self.text else self.placeholder
            text_color = self.style['text_color'] if self.text else self.style['placeholder_color']
            
            text_surface = font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(x=self.x + 5, y=self.y + 5)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            self.logger.warning(f"Failed to render textbox text: {e}")
    
    def _render_cursor(self, surface):
        """Render text cursor"""
        if not self.text:
            return
        
        try:
            font = pygame.font.Font(None, 20)
            text_before_cursor = self.text[:self.cursor_pos]
            text_surface = font.render(text_before_cursor, True, self.style['text_color'])
            cursor_x = self.x + 5 + text_surface.get_width()
            
            pygame.draw.line(surface, self.style['cursor_color'], 
                           (cursor_x, self.y + 5), (cursor_x, self.y + self.height - 5), 2)
        except Exception as e:
            self.logger.warning(f"Failed to render cursor: {e}")
    
    def handle_event(self, event) -> bool:
        """Handle text input events"""
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.focused = True
                return True
            else:
                self.focused = False
                return False
        
        elif event.type == pygame.KEYDOWN and self.focused:
            return self._handle_key_down(event)
        
        return False
    
    def _handle_key_down(self, event) -> bool:
        """Handle keyboard input"""
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
            return True
        
        elif event.key == pygame.K_DELETE:
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            return True
        
        elif event.key == pygame.K_LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            return True
        
        elif event.key == pygame.K_RIGHT:
            self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            return True
        
        elif event.key == pygame.K_RETURN:
            self.focused = False
            return True
        
        elif event.unicode.isprintable():
            self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
            self.cursor_pos += 1
            return True
        
        return False 