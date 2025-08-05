import pygame
import config

class DebugManager:
    """Handles debug mode and debug info display"""
    
    def __init__(self):
        self.debug_mode = config.DEFAULT_DEBUG_MODE
        self.font = None
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0
    
    def initialize_font(self):
        """Initialize font for debug info"""
        try:
            self.font = pygame.font.Font(None, config.DEBUG_FONT_SIZE)
        except:
            self.font = pygame.font.SysFont('arial', 18)
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        status = "ON" if self.debug_mode else "OFF"
        print(f"🐛 Debug mode: {status}")
        return self.debug_mode
    
    def update_fps(self, clock):
        """Update FPS calculation"""
        self.fps_counter += 1
        self.fps_timer += clock.get_time()
        
        # Update FPS every 500ms
        if self.fps_timer >= config.FPS_UPDATE_INTERVAL:
            self.current_fps = int((self.fps_counter * 1000) / self.fps_timer)
            self.fps_counter = 0
            self.fps_timer = 0
    
    def draw_debug_info(self, surface):
        """Draw debug info in top-left corner"""
        if not self.debug_mode or not self.font:
            return
        
        # Draw FPS
        fps_text = f"FPS: {self.current_fps}"
        text_surface = self.font.render(fps_text, True, config.DEBUG_TEXT_COLOR)
        
        # Position at top-left with small margin
        surface.blit(text_surface, (10, 10))
    
    def should_show_boundaries(self):
        """Check if boundaries should be shown"""
        return self.debug_mode
    
    def should_show_selection_box(self):
        """Check if selection box should be shown"""
        return self.debug_mode 