import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PANEL_WIDTH = 800
PANEL_HEIGHT = 600

# Colors (Tailwind to RGB conversion)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE_500 = (59, 130, 246)
GREEN_800 = (22, 101, 52)
YELLOW_800 = (133, 77, 14)
GRAY_300 = (209, 213, 219)
GRAY_500 = (107, 114, 128)
BORDER_COLOR = (229, 231, 235)

# Fonts
font_xl = pygame.font.Font(None, 24)  # text-xl
font_lg = pygame.font.Font(None, 20)  # text-lg
font_base = pygame.font.Font(None, 16)  # base text

class ControlPanel:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Control Panel")
        self.clock = pygame.time.Clock()
        
        # State
        self.selected_tab = "shimeji"  # shimeji, general, tiktok
        self.is_connected = False
        
        # Shimeji state
        self.spawn_count = 3
        
        # General state
        self.floor_value = 10
        self.ceiling_value = 90
        self.left_wall_value = 10
        self.right_wall_value = 90
        
        # TikTok state
        self.username_text = ""
        self.username_active = False
        
        # UI elements
        self.setup_ui_elements()
        
    def setup_ui_elements(self):
        # Panel rect
        self.panel_rect = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
        
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
        if font is None:
            font = font_base
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BORDER_COLOR, rect, 2)
        
        text_surface = font.render(text, True, text_color)
        if align_left:
            text_rect = text_surface.get_rect()
            text_rect.centery = rect.centery
            text_rect.x = rect.x + 10  # 10px padding from left
        else:
            text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_counter(self, x, y, value, title):
        # Title
        title_surface = font_lg.render(title, True, BLACK)
        self.screen.blit(title_surface, (x, y))
        
        # Counter elements
        minus_rect = pygame.Rect(x, y + 30, self.btn_width, self.btn_height)
        counter_rect = pygame.Rect(x + self.btn_width + 5, y + 30, self.counter_width, self.counter_height)
        plus_rect = pygame.Rect(x + self.btn_width + self.counter_width + 10, y + 30, self.btn_width, self.btn_height)
        
        # Draw buttons and counter
        self.draw_button(minus_rect, "-", WHITE, BLACK)
        self.draw_button(counter_rect, str(value), WHITE, BLACK)
        self.draw_button(plus_rect, "+", WHITE, BLACK)
        
        return minus_rect, plus_rect
        
    def draw_tabs(self):
        # Tab buttons
        tabs = [
            (self.shimeji_tab, "shimeji"),
            (self.general_tab, "general"), 
            (self.tiktok_tab, "tiktok")
        ]
        
        for rect, tab_name in tabs:
            if self.selected_tab == tab_name:
                color = BLUE_500
                text_color = WHITE
            else:
                color = WHITE
                text_color = BLACK
                
            self.draw_button(rect, tab_name, color, text_color, font_base, align_left=True)
            
        # Tab separator line
        pygame.draw.line(self.screen, BORDER_COLOR, (20, 80), (780, 80), 2)
        
    def draw_shimeji_content(self):
        # Initial Spawn section
        title_surface = font_xl.render("Initial Spawn", True, BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Counter
        self.shimeji_minus, self.shimeji_plus = self.draw_counter(30, 130, self.spawn_count, "spawn")
        
        # Section separator (moved down)
        pygame.draw.line(self.screen, GRAY_300, (30, 210), (770, 210), 1)
        
    def draw_general_content(self):
        # Boundaries section
        title_surface = font_xl.render("Boundaries", True, BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Floor and Ceiling
        self.floor_minus, self.floor_plus = self.draw_counter(30, 130, self.floor_value, "Floor")
        self.ceiling_minus, self.ceiling_plus = self.draw_counter(250, 130, self.ceiling_value, "Ceiling")
        
        # Gap between floor-ceiling and walls sections (added 20px gap)
        # Left Wall and Right Wall  
        self.left_wall_minus, self.left_wall_plus = self.draw_counter(30, 220, self.left_wall_value, "Left Wall")
        self.right_wall_minus, self.right_wall_plus = self.draw_counter(250, 220, self.right_wall_value, "Right Wall")
        
        # Section separator (moved down)
        pygame.draw.line(self.screen, GRAY_300, (30, 300), (770, 300), 1)
        
    def draw_tiktok_content(self):
        # Username section
        title_surface = font_xl.render("Username:", True, BLACK)
        self.screen.blit(title_surface, (30, 100))
        
        # Input field
        self.username_rect = pygame.Rect(30, 140, 300, 40)
        input_color = WHITE
        if self.username_active:
            pygame.draw.rect(self.screen, input_color, self.username_rect)
            pygame.draw.rect(self.screen, BLUE_500, self.username_rect, 2)
        else:
            pygame.draw.rect(self.screen, input_color, self.username_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, self.username_rect, 2)
            
        # Username text
        if self.username_text:
            text_surface = font_base.render(self.username_text, True, BLACK)
        else:
            text_surface = font_base.render("Masukkan username TikTok", True, GRAY_500)
        
        text_rect = text_surface.get_rect()
        text_rect.centery = self.username_rect.centery
        text_rect.x = self.username_rect.x + 10
        self.screen.blit(text_surface, text_rect)
        
        # Input info
        info_surface = font_base.render("input tanpa @", True, GRAY_500)
        self.screen.blit(info_surface, (30, 185))
        
        # Connect button
        self.connect_rect = pygame.Rect(350, 140, 120, 40)
        if self.is_connected:
            color = GREEN_800
            text = "Connected"
        else:
            color = YELLOW_800
            text = "Connect"
            
        self.draw_button(self.connect_rect, text, color, WHITE)
        
        # Section separator
        pygame.draw.line(self.screen, GRAY_300, (30, 220), (770, 220), 1)
        
    def handle_click(self, pos):
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
            elif hasattr(self, 'shimeji_plus') and self.shimeji_plus.collidepoint(pos):
                self.spawn_count += 1
                
        elif self.selected_tab == "general":
            # Floor controls
            if hasattr(self, 'floor_minus') and self.floor_minus.collidepoint(pos):
                self.floor_value = max(0, self.floor_value - 1)
            elif hasattr(self, 'floor_plus') and self.floor_plus.collidepoint(pos):
                self.floor_value += 1
                
            # Ceiling controls
            if hasattr(self, 'ceiling_minus') and self.ceiling_minus.collidepoint(pos):
                self.ceiling_value = max(0, self.ceiling_value - 1)
            elif hasattr(self, 'ceiling_plus') and self.ceiling_plus.collidepoint(pos):
                self.ceiling_value += 1
                
            # Left wall controls
            if hasattr(self, 'left_wall_minus') and self.left_wall_minus.collidepoint(pos):
                self.left_wall_value = max(0, self.left_wall_value - 1)
            elif hasattr(self, 'left_wall_plus') and self.left_wall_plus.collidepoint(pos):
                self.left_wall_value += 1
                
            # Right wall controls
            if hasattr(self, 'right_wall_minus') and self.right_wall_minus.collidepoint(pos):
                self.right_wall_value = max(0, self.right_wall_value - 1)
            elif hasattr(self, 'right_wall_plus') and self.right_wall_plus.collidepoint(pos):
                self.right_wall_value += 1
                
        elif self.selected_tab == "tiktok":
            # Username input
            if hasattr(self, 'username_rect') and self.username_rect.collidepoint(pos):
                self.username_active = True
            else:
                self.username_active = False
                
            # Connect button
            if hasattr(self, 'connect_rect') and self.connect_rect.collidepoint(pos):
                self.is_connected = not self.is_connected
                
    def handle_keydown(self, event):
        if self.selected_tab == "tiktok" and self.username_active:
            if event.key == pygame.K_BACKSPACE:
                self.username_text = self.username_text[:-1]
            else:
                # Only allow alphanumeric and some special characters
                if event.unicode.isprintable() and len(self.username_text) < 30:
                    self.username_text += event.unicode
                    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                    
            # Clear screen
            self.screen.fill(WHITE)
            
            # Draw panel border
            pygame.draw.rect(self.screen, WHITE, self.panel_rect)
            pygame.draw.rect(self.screen, BORDER_COLOR, self.panel_rect, 2)
            
            # Draw tabs
            self.draw_tabs()
            
            # Draw content based on selected tab
            if self.selected_tab == "shimeji":
                self.draw_shimeji_content()
            elif self.selected_tab == "general":
                self.draw_general_content()
            elif self.selected_tab == "tiktok":
                self.draw_tiktok_content()
                
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    panel = ControlPanel()
    panel.run()