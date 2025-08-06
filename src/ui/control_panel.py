import pygame
from ..utils.settings_manager import SettingsManager

class ControlPanel:
    """Control Panel with modern UI design from contohControlPanel.py"""
    
    def __init__(self, screen_width, screen_height, settings_manager: SettingsManager):
        self.visible = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings_manager = settings_manager
        
        # Panel dimensions and position
        self.panel_width = 800
        self.panel_height = 600
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        
        # Colors (Tailwind to RGB conversion from contohControlPanel.py)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE_500 = (59, 130, 246)
        self.GREEN_800 = (22, 101, 52)
        self.YELLOW_800 = (133, 77, 14)
        self.GRAY_300 = (209, 213, 219)
        self.GRAY_500 = (107, 114, 128)
        self.BORDER_COLOR = (229, 231, 235)
        
        # Fonts
        self.font_xl = pygame.font.Font(None, 24)  # text-xl
        self.font_lg = pygame.font.Font(None, 20)  # text-lg
        self.font_base = pygame.font.Font(None, 16)  # base text
        
        # State
        self.selected_tab = "shimeji"  # shimeji, general, tiktok
        self.is_connected = False
        
        # Shimeji state
        self.spawn_count = self.settings_manager.get_setting('ui.initial_pet_count', 3)
        
        # General state
        self.floor_value = self.settings_manager.get_setting('boundaries.floor_margin', 10)
        self.ceiling_value = self.settings_manager.get_setting('boundaries.ceiling_margin', 10)
        self.left_wall_value = self.settings_manager.get_setting('boundaries.wall_left_margin', 10)
        self.right_wall_value = self.settings_manager.get_setting('boundaries.wall_right_margin', 90)
        
        # TikTok state
        self.username_text = self.settings_manager.get_setting('tiktok.username', '')
        self.username_active = False
        
        # UI elements
        self.setup_ui_elements()
        
    def setup_ui_elements(self):
        """Setup UI elements from contohControlPanel.py"""
        # Panel rect
        self.panel_rect = pygame.Rect(0, 0, self.panel_width, self.panel_height)
        
        # Tab buttons
        tab_width = 266
        tab_height = 40
        tab_y = 20
        
        self.shimeji_tab = pygame.Rect(67, tab_y, tab_width, tab_height)
        self.general_tab = pygame.Rect(267, tab_y, tab_width, tab_height)
        self.tiktok_tab = pygame.Rect(467, tab_y, tab_width, tab_height)
        
        # Button dimensions
        self.btn_width = 40
        self.btn_height = 40
        self.counter_width = 120
        self.counter_height = 40
        
    def draw_button(self, rect, text, color, text_color, font=None, align_left=False):
        """Draw button with styling from contohControlPanel.py"""
        if font is None:
            font = self.font_base
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, rect, 2)
        
        text_surface = font.render(text, True, text_color)
        if align_left:
            text_rect = text_surface.get_rect()
            text_rect.centery = rect.centery
            text_rect.x = rect.x + 10  # 10px padding from left
        else:
            text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_counter(self, x, y, value, title):
        """Draw counter with +/- buttons from contohControlPanel.py"""
        # Title
        title_surface = self.font_lg.render(title, True, self.BLACK)
        self.screen.blit(title_surface, (x, y))
        
        # Counter elements
        minus_rect = pygame.Rect(x, y + 30, self.btn_width, self.btn_height)
        counter_rect = pygame.Rect(x + self.btn_width + 5, y + 30, self.counter_width, self.counter_height)
        plus_rect = pygame.Rect(x + self.btn_width + self.counter_width + 10, y + 30, self.btn_width, self.btn_height)
        
        # Draw buttons and counter
        self.draw_button(minus_rect, "-", self.WHITE, self.BLACK)
        self.draw_button(counter_rect, str(value), self.WHITE, self.BLACK)
        self.draw_button(plus_rect, "+", self.WHITE, self.BLACK)
        
        return minus_rect, plus_rect
        
    def draw_tabs(self):
        """Draw tabs from contohControlPanel.py"""
        # Tab buttons
        tabs = [
            (self.shimeji_tab, "shimeji"),
            (self.general_tab, "general"), 
            (self.tiktok_tab, "tiktok")
        ]
        
        for rect, tab_name in tabs:
            if self.selected_tab == tab_name:
                color = self.BLUE_500
                text_color = self.WHITE
            else:
                color = self.WHITE
                text_color = self.BLACK
                
            self.draw_button(rect, tab_name, color, text_color, self.font_base, align_left=True)
            
        # Tab separator line
        pygame.draw.line(self.screen, self.BORDER_COLOR, (20, 80), (780, 80), 2)
        
    def draw_shimeji_content(self):
        """Draw shimeji tab content from contohControlPanel.py"""
        # Initial Spawn section
        title_surface = self.font_xl.render("Initial Spawn", True, self.BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Counter
        self.shimeji_minus, self.shimeji_plus = self.draw_counter(30, 130, self.spawn_count, "spawn")
        
        # Section separator (moved down)
        pygame.draw.line(self.screen, self.GRAY_300, (30, 210), (770, 210), 1)
        
    def draw_general_content(self):
        """Draw general tab content from contohControlPanel.py"""
        # Boundaries section
        title_surface = self.font_xl.render("Boundaries", True, self.BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Floor and Ceiling
        self.floor_minus, self.floor_plus = self.draw_counter(30, 130, self.floor_value, "Floor")
        self.ceiling_minus, self.ceiling_plus = self.draw_counter(250, 130, self.ceiling_value, "Ceiling")
        
        # Gap between floor-ceiling and walls sections (added 20px gap)
        # Left Wall and Right Wall  
        self.left_wall_minus, self.left_wall_plus = self.draw_counter(30, 220, self.left_wall_value, "Left Wall")
        self.right_wall_minus, self.right_wall_plus = self.draw_counter(250, 220, self.right_wall_value, "Right Wall")
        
        # Section separator (moved down)
        pygame.draw.line(self.screen, self.GRAY_300, (30, 300), (770, 300), 1)
        
    def draw_tiktok_content(self):
        """Draw tiktok tab content from contohControlPanel.py"""
        # Username section
        title_surface = self.font_xl.render("Username:", True, self.BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Input field
        self.username_rect = pygame.Rect(30, 140, 300, 40)
        input_color = self.WHITE
        if self.username_active:
            pygame.draw.rect(self.screen, input_color, self.username_rect)
            pygame.draw.rect(self.screen, self.BLUE_500, self.username_rect, 2)
        else:
            pygame.draw.rect(self.screen, input_color, self.username_rect)
            pygame.draw.rect(self.screen, self.BORDER_COLOR, self.username_rect, 2)
            
        # Username text
        if self.username_text:
            text_surface = self.font_base.render(self.username_text, True, self.BLACK)
        else:
            text_surface = self.font_base.render("Masukkan username TikTok", True, self.GRAY_500)
        
        text_rect = text_surface.get_rect()
        text_rect.centery = self.username_rect.centery
        text_rect.x = self.username_rect.x + 10
        self.screen.blit(text_surface, text_rect)
        
        # Input info
        info_surface = self.font_base.render("input tanpa @", True, self.GRAY_500)
        self.screen.blit(info_surface, (30, 185))
        
        # Connect button
        self.connect_rect = pygame.Rect(350, 140, 120, 40)
        if self.is_connected:
            color = self.GREEN_800
            text = "Connected"
        else:
            color = self.YELLOW_800
            text = "Connect"
            
        self.draw_button(self.connect_rect, text, color, self.WHITE)
        
        # Section separator
        pygame.draw.line(self.screen, self.GRAY_300, (30, 220), (770, 220), 1)
        
    def handle_click(self, pos):
        """Handle mouse clicks from contohControlPanel.py"""
        # Tab clicks
        if self.shimeji_tab.collidepoint(pos):
            self.selected_tab = "shimeji"
        elif self.general_tab.collidepoint(pos):
            self.selected_tab = "general"
        elif self.tiktok_tab.collidepoint(pos):
            self.selected_tab = "tiktok"
            
        # Content clicks based on selected tab
        if self.selected_tab == "shimeji":
            if hasattr(self, 'shimeji_minus') and self.shimeji_minus.collidepoint(pos):
                self.spawn_count = max(0, self.spawn_count - 1)
                self.settings_manager.set_setting('ui.initial_pet_count', self.spawn_count)
                self.settings_manager.save_settings()
            elif hasattr(self, 'shimeji_plus') and self.shimeji_plus.collidepoint(pos):
                self.spawn_count += 1
                self.settings_manager.set_setting('ui.initial_pet_count', self.spawn_count)
                self.settings_manager.save_settings()
                
        elif self.selected_tab == "general":
            # Floor controls
            if hasattr(self, 'floor_minus') and self.floor_minus.collidepoint(pos):
                self.floor_value = max(0, self.floor_value - 1)
                self.settings_manager.set_setting('boundaries.floor_margin', self.floor_value)
                self.settings_manager.save_settings()
            elif hasattr(self, 'floor_plus') and self.floor_plus.collidepoint(pos):
                self.floor_value += 1
                self.settings_manager.set_setting('boundaries.floor_margin', self.floor_value)
                self.settings_manager.save_settings()
                
            # Ceiling controls
            if hasattr(self, 'ceiling_minus') and self.ceiling_minus.collidepoint(pos):
                self.ceiling_value = max(0, self.ceiling_value - 1)
                self.settings_manager.set_setting('boundaries.ceiling_margin', self.ceiling_value)
                self.settings_manager.save_settings()
            elif hasattr(self, 'ceiling_plus') and self.ceiling_plus.collidepoint(pos):
                self.ceiling_value += 1
                self.settings_manager.set_setting('boundaries.ceiling_margin', self.ceiling_value)
                self.settings_manager.save_settings()
                
            # Left wall controls
            if hasattr(self, 'left_wall_minus') and self.left_wall_minus.collidepoint(pos):
                self.left_wall_value = max(0, self.left_wall_value - 1)
                self.settings_manager.set_setting('boundaries.wall_left_margin', self.left_wall_value)
                self.settings_manager.save_settings()
            elif hasattr(self, 'left_wall_plus') and self.left_wall_plus.collidepoint(pos):
                self.left_wall_value += 1
                self.settings_manager.set_setting('boundaries.wall_left_margin', self.left_wall_value)
                self.settings_manager.save_settings()
                
            # Right wall controls
            if hasattr(self, 'right_wall_minus') and self.right_wall_minus.collidepoint(pos):
                self.right_wall_value = max(0, self.right_wall_value - 1)
                self.settings_manager.set_setting('boundaries.wall_right_margin', self.right_wall_value)
                self.settings_manager.save_settings()
            elif hasattr(self, 'right_wall_plus') and self.right_wall_plus.collidepoint(pos):
                self.right_wall_value += 1
                self.settings_manager.set_setting('boundaries.wall_right_margin', self.right_wall_value)
                self.settings_manager.save_settings()
                
        elif self.selected_tab == "tiktok":
            # Username input
            if hasattr(self, 'username_rect') and self.username_rect.collidepoint(pos):
                self.username_active = True
            else:
                self.username_active = False
                
            # Connect button
            if hasattr(self, 'connect_rect') and self.connect_rect.collidepoint(pos):
                self.is_connected = not self.is_connected
                if self.username_text:
                    self.settings_manager.set_setting('tiktok.username', self.username_text)
                    self.settings_manager.save_settings()
                    
    def handle_keydown(self, event):
        """Handle keyboard input from contohControlPanel.py"""
        if self.selected_tab == "tiktok" and self.username_active:
            if event.key == pygame.K_BACKSPACE:
                self.username_text = self.username_text[:-1]
            else:
                # Only allow alphanumeric and some special characters
                if event.unicode.isprintable() and len(self.username_text) < 30:
                    self.username_text += event.unicode
                    
    def toggle_visibility(self):
        """Toggle control panel visibility"""
        self.visible = not self.visible
        return self.visible
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks for the control panel"""
        if not self.visible:
            return None
        
        # Check if click is within panel bounds
        if not self._is_point_in_panel(pos):
            return None
        
        # Convert global coordinates to panel-relative coordinates
        panel_pos = (pos[0] - self.panel_x, pos[1] - self.panel_y)
        
        # Handle the click with panel-relative coordinates
        self.handle_click(panel_pos)
        return None
    
    def _is_point_in_panel(self, pos):
        """Check if point is within panel bounds"""
        return (self.panel_x <= pos[0] <= self.panel_x + self.panel_width and
                self.panel_y <= pos[1] <= self.panel_y + self.panel_height)
    
    def handle_input(self, event):
        """Handle input events for the control panel"""
        if not self.visible:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.handle_mouse_click(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_keydown(event)
            if event.key == pygame.K_ESCAPE:
                self.visible = False
                return "close_panel"
        
        return None
    
    def render(self, surface):
        """Render control panel with modern design from contohControlPanel.py"""
        if not self.visible:
            return
        
        # Create a temporary surface for the panel
        self.screen = pygame.Surface((self.panel_width, self.panel_height))
        self.screen.fill(self.WHITE)
        
        # Draw panel border
        pygame.draw.rect(self.screen, self.WHITE, self.panel_rect)
        pygame.draw.rect(self.screen, self.BORDER_COLOR, self.panel_rect, 2)
        
        # Draw tabs
        self.draw_tabs()
        
        # Draw content based on selected tab
        if self.selected_tab == "shimeji":
            self.draw_shimeji_content()
        elif self.selected_tab == "general":
            self.draw_general_content()
        elif self.selected_tab == "tiktok":
            self.draw_tiktok_content()
        
        # Blit the panel surface to the main surface
        surface.blit(self.screen, (self.panel_x, self.panel_y)) 