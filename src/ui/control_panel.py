import pygame
import config

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
        
        # Tab dimensions
        self.tab_width = self.panel_width // len(self.tabs)
        self.tab_height = 40  # Increased tab height
        
        # Colors
        self.panel_bg = (40, 40, 40)
        self.tab_bg = (60, 60, 60)
        self.tab_active = (80, 80, 80)
        self.text_color = (255, 255, 255)
        self.button_color = (100, 100, 100)
        self.button_hover = (120, 120, 120)
        
        # Font
        self.font = None
        self.small_font = None
        self._initialize_fonts()
        
        # Interactive elements
        self.buttons = {}
        self._create_buttons()
        
        # Settings
        self.settings = {
            'volume': 70,
            'debug_mode': True,
            'boundaries': True,
            'auto_save': True
        }
    
    def _initialize_fonts(self):
        """Initialize fonts for the control panel"""
        try:
            self.font = pygame.font.Font(None, 28)  # Increased font size
            self.small_font = pygame.font.Font(None, 20)  # Increased small font size
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 18)
    
    def _create_buttons(self):
        """Create interactive buttons for the control panel with better spacing"""
        # Pets tab buttons - better spacing
        button_y = self.panel_y + 80  # Increased top margin
        button_spacing = 120  # Increased spacing between buttons
        
        self.buttons['add_pet'] = {
            'rect': pygame.Rect(self.panel_x + 30, button_y, 120, 35),
            'text': 'Add Pet',
            'tab': 'pets',
            'action': 'add_pet'
        }
        
        self.buttons['remove_pet'] = {
            'rect': pygame.Rect(self.panel_x + 30 + button_spacing, button_y, 120, 35),
            'text': 'Remove Pet',
            'tab': 'pets',
            'action': 'remove_pet'
        }
        
        self.buttons['clear_all'] = {
            'rect': pygame.Rect(self.panel_x + 30 + button_spacing * 2, button_y, 120, 35),
            'text': 'Clear All',
            'tab': 'pets',
            'action': 'clear_all'
        }
        
        # Settings tab buttons - moved to lower position to avoid text collision
        settings_button_y = self.panel_y + 280  # Much lower position for settings buttons
        self.buttons['toggle_debug'] = {
            'rect': pygame.Rect(self.panel_x + 30, settings_button_y, 140, 35),
            'text': 'Debug Mode',
            'tab': 'settings',
            'action': 'toggle_debug'
        }
        
        self.buttons['toggle_boundaries'] = {
            'rect': pygame.Rect(self.panel_x + 30 + button_spacing, settings_button_y, 140, 35),
            'text': 'Boundaries',
            'tab': 'settings',
            'action': 'toggle_boundaries'
        }
        
        # TikTok tab buttons - better spacing
        tiktok_button_y = self.panel_y + 160  # Original position for TikTok buttons
        self.buttons['connect_tiktok'] = {
            'rect': pygame.Rect(self.panel_x + 30, tiktok_button_y, 140, 35),
            'text': 'Connect',
            'tab': 'tiktok',
            'action': 'connect_tiktok'
        }
        
        self.buttons['disconnect_tiktok'] = {
            'rect': pygame.Rect(self.panel_x + 30 + button_spacing, tiktok_button_y, 140, 35),
            'text': 'Disconnect',
            'tab': 'tiktok',
            'action': 'disconnect_tiktok'
        }
    
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
        for button_id, button in self.buttons.items():
            if (button['tab'] == self.active_tab and 
                button['rect'].collidepoint(pos)):
                return button['action']
        return None
    
    def render(self, surface):
        """Render control panel"""
        if not self.visible:
            return
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Draw panel background
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(surface, self.panel_bg, panel_rect)
        pygame.draw.rect(surface, (255, 255, 255), panel_rect, 2)
        
        # Draw tabs
        self._draw_tabs(surface)
        
        # Draw content based on active tab
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
            pet_info = f"Current Pets: {len(self.buttons)} available actions"
            info_surface = self.small_font.render(pet_info, True, (200, 200, 200))
            surface.blit(info_surface, (self.panel_x + 30, start_y + 40))
        
        # Draw buttons for pets tab
        for button_id, button in self.buttons.items():
            if button['tab'] == 'pets':
                self._draw_button(surface, button)
    
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
        for button_id, button in self.buttons.items():
            if button['tab'] == 'settings':
                self._draw_button(surface, button)
    
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
        for button_id, button in self.buttons.items():
            if button['tab'] == 'tiktok':
                self._draw_button(surface, button)
    
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