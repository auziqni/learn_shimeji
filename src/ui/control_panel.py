import pygame
from ui.ui_components import Button, Panel, Slider, TextBox

class ControlPanel:
    """In-game control panel for settings and management"""
    
    def __init__(self, screen_width, screen_height):
        self.visible = False
        self.active_tab = "pets"
        self.tabs = ["pets", "settings", "tiktok", "logs"]
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Panel dimensions and position (expanded)
        self.panel_width = 700
        self.panel_height = 500
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # Create main panel using new UI components
        self.main_panel = Panel(self.panel_x, self.panel_y, self.panel_width, self.panel_height, "Control Panel")
        
        # Add tabs to panel
        for tab_name in self.tabs:
            self.main_panel.add_tab(tab_name)
        
        # Font
        self.font = None
        self.small_font = None
        self._initialize_fonts()
        
        # Settings (must be initialized before UI components)
        self.settings = {
            'volume': 70,
            'debug_mode': True,
            'boundaries': True,
            'auto_save': True
        }
        
        # Create UI components
        self.ui_components = {}
        self._create_ui_components()
    
    def _initialize_fonts(self):
        """Initialize fonts for the control panel"""
        try:
            self.font = pygame.font.Font(None, 28)  # Increased font size
            self.small_font = pygame.font.Font(None, 20)  # Increased small font size
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 18)
    
    def _create_ui_components(self):
        """Create UI components for the control panel"""
        # Pets tab buttons
        button_y = self.panel_y + 80
        button_spacing = 120
        
        # Add Pet button
        add_pet_btn = Button(self.panel_x + 30, button_y, 120, 35, "Add Pet")
        self.ui_components['add_pet'] = add_pet_btn
        self.main_panel.add_button(add_pet_btn)
        
        # Remove Pet button
        remove_pet_btn = Button(self.panel_x + 30 + button_spacing, button_y, 120, 35, "Remove Pet")
        self.ui_components['remove_pet'] = remove_pet_btn
        self.main_panel.add_button(remove_pet_btn)
        
        # Clear All button
        clear_all_btn = Button(self.panel_x + 30 + button_spacing * 2, button_y, 120, 35, "Clear All")
        self.ui_components['clear_all'] = clear_all_btn
        self.main_panel.add_button(clear_all_btn)
        
        # Settings tab components
        settings_y = self.panel_y + 280
        
        # Debug Mode button
        debug_btn = Button(self.panel_x + 30, settings_y, 140, 35, "Debug Mode")
        self.ui_components['toggle_debug'] = debug_btn
        self.main_panel.add_button(debug_btn)
        
        # Boundaries button
        boundaries_btn = Button(self.panel_x + 30 + button_spacing, settings_y, 140, 35, "Boundaries")
        self.ui_components['toggle_boundaries'] = boundaries_btn
        self.main_panel.add_button(boundaries_btn)
        
        # Volume slider
        volume_slider = Slider(self.panel_x + 30, settings_y + 60, 200, 20, 0, 100, self.settings['volume'])
        self.ui_components['volume_slider'] = volume_slider
        self.main_panel.add_button(volume_slider)
        
        # TikTok tab buttons
        tiktok_button_y = self.panel_y + 160
        
        # Connect TikTok button
        connect_tiktok_btn = Button(self.panel_x + 30, tiktok_button_y, 140, 35, "Connect")
        self.ui_components['connect_tiktok'] = connect_tiktok_btn
        self.main_panel.add_button(connect_tiktok_btn)
        
        # Disconnect TikTok button
        disconnect_tiktok_btn = Button(self.panel_x + 30 + button_spacing, tiktok_button_y, 140, 35, "Disconnect")
        self.ui_components['disconnect_tiktok'] = disconnect_tiktok_btn
        self.main_panel.add_button(disconnect_tiktok_btn)
    
    def toggle_visibility(self):
        """Toggle control panel visibility"""
        self.visible = not self.visible
        return self.visible
    
    def switch_tab(self, tab_name):
        """Switch to different tab"""
        if tab_name in self.tabs:
            self.active_tab = tab_name
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on the control panel"""
        if not self.visible:
            return None
        
        # Check if click is within panel bounds
        if not self._is_point_in_panel(pos):
            return None
        
        # Check tab clicks
        if self._handle_tab_click(pos):
            return None
        
        # Check button clicks
        return self._handle_button_click(pos)
    
    def _is_point_in_panel(self, pos):
        """Check if point is within panel bounds"""
        return (self.panel_x <= pos[0] <= self.panel_x + self.panel_width and
                self.panel_y <= pos[1] <= self.panel_y + self.panel_height)
    
    def _handle_tab_click(self, pos):
        """Handle tab clicks"""
        if pos[1] < self.panel_y + self.tab_height:
            tab_x = pos[0] - self.panel_x
            tab_index = int(tab_x // self.tab_width)
            if 0 <= tab_index < len(self.tabs):
                self.active_tab = self.tabs[tab_index]
                return True
        return False
    
    def _handle_button_click(self, pos):
        """Handle button clicks"""
        for button_id, component in self.ui_components.items():
            if hasattr(component, 'rect') and component.rect.collidepoint(pos):
                return button_id
        return None
    
    def render(self, surface):
        """Render control panel using new UI components"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Render main panel using new UI components
        self.main_panel.render(surface)
        
        # Draw additional content based on active tab
        self._draw_tab_content(surface)
    
    def _draw_tabs(self, surface):
        """Draw tab buttons"""
        for i, tab_name in enumerate(self.tabs):
            tab_x = self.panel_x + (i * self.tab_width)
            tab_rect = pygame.Rect(tab_x, self.panel_y, self.tab_width, self.tab_height)
            
            # Choose color based on active state
            color = self.tab_active if tab_name == self.active_tab else self.tab_bg
            pygame.draw.rect(surface, color, tab_rect)
            pygame.draw.rect(surface, (255, 255, 255), tab_rect, 1)
            
            # Draw tab text
            if self.font:
                text_surface = self.font.render(tab_name.title(), True, self.text_color)
                text_rect = text_surface.get_rect(center=tab_rect.center)
                surface.blit(text_surface, text_rect)
    
    def _draw_tab_content(self, surface):
        """Draw content for the active tab with better spacing"""
        content_y = self.panel_y + self.tab_height + 20  # Increased top margin
        
        if self.active_tab == "pets":
            self._draw_pets_tab(surface, content_y)
        elif self.active_tab == "settings":
            self._draw_settings_tab(surface, content_y)
        elif self.active_tab == "tiktok":
            self._draw_tiktok_tab(surface, content_y)
        elif self.active_tab == "logs":
            self._draw_logs_tab(surface, content_y)
    
    def _draw_pets_tab(self, surface, start_y):
        """Draw pets tab content with better spacing"""
        if not self.font:
            return
        
        # Title with better spacing
        title = self.font.render("Pet Management", True, self.text_color)
        surface.blit(title, (self.panel_x + 30, start_y))
        
        # Pet count info with better spacing
        if self.small_font:
            pet_info = f"Current Pets: {len(self.ui_components)} available actions"
            info_surface = self.small_font.render(pet_info, True, (200, 200, 200))
            surface.blit(info_surface, (self.panel_x + 30, start_y + 40))
        
        # Draw buttons for pets tab
        for button_id, component in self.ui_components.items():
            if hasattr(component, 'render'):
                component.render(surface)
    
    def _draw_settings_tab(self, surface, start_y):
        """Draw settings tab content with better spacing"""
        if not self.font:
            return
        
        # Title with better spacing
        title = self.font.render("Settings", True, self.text_color)
        surface.blit(title, (self.panel_x + 30, start_y))
        
        # Settings info with better spacing - limited to avoid button collision
        if self.small_font:
            y_offset = start_y + 60  # Increased spacing from title
            settings_to_show = list(self.settings.items())[:3]  # Only show first 3 settings to avoid collision
            
            for setting, value in settings_to_show:
                text = f"{setting.replace('_', ' ').title()}: {value}"
                text_surface = self.small_font.render(text, True, self.text_color)
                surface.blit(text_surface, (self.panel_x + 30, y_offset))
                y_offset += 40  # Increased line spacing to 40px
            
            # Add a separator line
            separator_y = y_offset + 20
            pygame.draw.line(surface, (100, 100, 100), 
                           (self.panel_x + 30, separator_y), 
                           (self.panel_x + self.panel_width - 30, separator_y), 2)
            
            # Add note about button position
            note_text = "Use buttons below to control settings"
            note_surface = self.small_font.render(note_text, True, (150, 150, 150))
            surface.blit(note_surface, (self.panel_x + 30, separator_y + 20))
        
        # Draw buttons for settings tab
        for button_id, component in self.ui_components.items():
            if hasattr(component, 'render'):
                component.render(surface)
    
    def _draw_tiktok_tab(self, surface, start_y):
        """Draw TikTok tab content with better spacing"""
        if not self.font:
            return
        
        # Title with better spacing
        title = self.font.render("TikTok Integration", True, self.text_color)
        surface.blit(title, (self.panel_x + 30, start_y))
        
        # Status info with better spacing
        if self.small_font:
            status_text = "Status: Not Connected"
            status_surface = self.small_font.render(status_text, True, (255, 100, 100))
            surface.blit(status_surface, (self.panel_x + 30, start_y + 60))
            
            # Additional info with better spacing
            info_text = "Connect to TikTok Live for real-time interaction"
            info_surface = self.small_font.render(info_text, True, (200, 200, 200))
            surface.blit(info_surface, (self.panel_x + 30, start_y + 95))
        
        # Draw buttons for TikTok tab
        for button_id, component in self.ui_components.items():
            if hasattr(component, 'render'):
                component.render(surface)
    
    def _draw_logs_tab(self, surface, start_y):
        """Draw logs tab content with better spacing"""
        if not self.font:
            return
        
        # Title with better spacing
        title = self.font.render("System Logs", True, self.text_color)
        surface.blit(title, (self.panel_x + 30, start_y))
        
        # Sample log entries with better spacing
        if self.small_font:
            logs = [
                "System initialized successfully",
                "Loaded 3 pets",
                "Debug mode enabled",
                "Window transparency applied",
                "Control panel ready",
                "Asset loading completed"
            ]
            
            y_offset = start_y + 60  # Increased spacing from title
            for log in logs:
                text_surface = self.small_font.render(log, True, self.text_color)
                surface.blit(text_surface, (self.panel_x + 30, y_offset))
                y_offset += 30  # Increased line spacing
    
    def _draw_button(self, surface, button):
        """Draw a button with better styling"""
        color = self.button_color
        pygame.draw.rect(surface, color, button['rect'])
        pygame.draw.rect(surface, (255, 255, 255), button['rect'], 1)
        
        if self.small_font:
            text_surface = self.small_font.render(button['text'], True, self.text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            surface.blit(text_surface, text_rect)
    
    def handle_input(self, event):
        """Handle control panel input"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_mouse_click(event.pos)
        return None 