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
        
        # Draw performance stats if available
        try:
            from utils.performance_monitor import performance_monitor
            perf_stats = performance_monitor.get_performance_stats()
            
            # Frame time
            frame_time_text = f"Frame: {perf_stats['frame_time']:.1f}ms"
            frame_time_surface = self.font.render(frame_time_text, True, (200, 200, 200))
            surface.blit(frame_time_surface, (10, 35))
            
            # CPU usage
            cpu_text = f"CPU: {perf_stats['cpu_usage']:.1f}%"
            cpu_surface = self.font.render(cpu_text, True, (200, 200, 200))
            surface.blit(cpu_surface, (10, 60))
            
            # Memory info
            from utils.memory_manager import memory_manager
            mem_stats = memory_manager.get_memory_stats()
            mem_text = f"Mem: {mem_stats['current_memory_mb']:.1f}MB"
            mem_surface = self.font.render(mem_text, True, (200, 200, 200))
            surface.blit(mem_surface, (10, 85))
            
            # Alerts count
            if perf_stats['alerts'] > 0:
                alert_text = f"Alerts: {perf_stats['alerts']}"
                alert_surface = self.font.render(alert_text, True, (255, 200, 200))
                surface.blit(alert_surface, (10, 110))
                
        except Exception as e:
            # Silently fail if performance monitoring is not available
            pass
    
    def should_show_boundaries(self):
        """Check if boundaries should be shown"""
        return self.debug_mode
    
    def should_show_selection_box(self):
        """Check if selection box should be shown"""
        return self.debug_mode 