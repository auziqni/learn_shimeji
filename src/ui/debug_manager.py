import pygame

class DebugManager:
    """Handles debug mode and debug info display"""
    
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.debug_mode = self.settings_manager.get_setting('ui.debug_mode', True) if self.settings_manager else True
        self.font = None
        self.fps_counter = 0
        self.fps_timer = 0
        self.current_fps = 0
    
    def initialize_font(self):
        """Initialize font for debug info"""
        debug_font_size = self.settings_manager.get_setting('ui.debug_font_size', 18) if self.settings_manager else 18
        try:
            self.font = pygame.font.Font(None, debug_font_size)
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
        fps_update_interval = self.settings_manager.get_setting('ui.fps_update_interval', 500) if self.settings_manager else 500
        if self.fps_timer >= fps_update_interval:
            self.current_fps = int((self.fps_counter * 1000) / self.fps_timer)
            self.fps_counter = 0
            self.fps_timer = 0
    
    def draw_debug_info(self, surface):
        """Draw debug info in top-left corner"""
        if not self.debug_mode or not self.font:
            return
        
        # Draw FPS
        fps_text = f"FPS: {self.current_fps}"
        debug_text_color = self.settings_manager.get_setting('ui.debug_text_color', [255, 255, 255]) if self.settings_manager else [255, 255, 255]
        text_surface = self.font.render(fps_text, True, debug_text_color)
        
        # Position at top-left with small margin
        surface.blit(text_surface, (10, 10))
    
    def should_show_boundaries(self):
        """Check if boundaries should be shown"""
        return self.debug_mode
    
    def should_show_selection_box(self):
        """Check if selection box should be shown"""
        return self.debug_mode 