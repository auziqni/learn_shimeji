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
        
        # Colors
        debug_text_color = (0, 0, 0)  # Black text for white background
        secondary_color = (50, 50, 50)  # Dark gray for secondary info
        alert_color = (150, 0, 0)  # Dark red for alerts
        background_color = (255, 255, 255)  # White background
        
        # Collect all text surfaces and positions
        text_surfaces = []
        
        # FPS
        fps_text = f"FPS: {self.current_fps}"
        fps_surface = self.font.render(fps_text, True, debug_text_color)
        text_surfaces.append((fps_surface, (10, 10)))
        
        # Draw performance stats if available
        try:
            from ..utils.performance_monitor import performance_monitor
            perf_stats = performance_monitor.get_performance_stats()
            
            # Frame time
            frame_time_text = f"Frame: {perf_stats['frame_time']:.1f}ms"
            frame_time_surface = self.font.render(frame_time_text, True, secondary_color)
            text_surfaces.append((frame_time_surface, (10, 35)))
            
            # CPU usage
            cpu_text = f"CPU: {perf_stats['cpu_usage']:.1f}%"
            cpu_surface = self.font.render(cpu_text, True, secondary_color)
            text_surfaces.append((cpu_surface, (10, 60)))
            
            # Memory info
            from ..utils.memory_manager import memory_manager
            mem_stats = memory_manager.get_memory_stats()
            mem_text = f"Mem: {mem_stats['current_memory_mb']:.1f}MB"
            mem_surface = self.font.render(mem_text, True, secondary_color)
            text_surfaces.append((mem_surface, (10, 85)))
            
            # Alerts count
            if perf_stats['alerts'] > 0:
                alert_text = f"Alerts: {perf_stats['alerts']}"
                alert_surface = self.font.render(alert_text, True, alert_color)
                text_surfaces.append((alert_surface, (10, 110)))
                
        except Exception as e:
            # Silently fail if performance monitoring is not available
            pass
        
        # Calculate background size
        if text_surfaces:
            max_width = max(surface.get_width() for surface, _ in text_surfaces)
            total_height = len(text_surfaces) * 25 + 20  # 25px per line + 20px padding
            
            # Draw white background with padding
            background_rect = pygame.Rect(0, 0, max_width + 20, total_height)
            pygame.draw.rect(surface, background_color, background_rect)
            
            # Draw all text surfaces
            for text_surface, pos in text_surfaces:
                surface.blit(text_surface, pos)
    
    def draw_pet_debug_info(self, surface, pet, pet_index):
        """Draw debug info for a specific pet to the right of the pet"""
        if not self.debug_mode or not self.font or not pet:
            return
        
        # Get pet data
        sprite_name = pet.get_current_sprite_pack()
        pet_name = pet.get_name()
        chat = pet.get_chat()
        position = pet.get_position()
        direction = pet.get_direction()
        position_state_text = pet.get_position_state_text()
        
        # Calculate position for debug info (to the right of pet)
        pet_x, pet_y = position
        pet_width = pet.width
        debug_x = pet_x + pet_width + 10  # 10px to the right of pet
        debug_y = pet_y
        
        # Colors for different info types
        sprite_color = (255, 255, 0)    # Yellow for sprite name
        chat_color = (255, 255, 255)    # White for chat/action
        pos_color = (255, 200, 200)     # Light red for position
        dir_color = (0, 255, 255)       # Cyan for direction
        state_color = (255, 200, 255)   # Light purple for position state
        background_color = (0, 0, 0)    # Black background
        
        # Line spacing
        line_height = 20
        current_y = debug_y
        
        # Collect all text surfaces and positions
        text_surfaces = []
        
        try:
            # Line 1: Sprite Name : Pet Name (always show both)
            combined_text = f"{sprite_name} : {pet_name}"
            
            # Truncate if too long
            if len(combined_text) > 30:
                combined_text = combined_text[:27] + "..."
            
            combined_surface = self.font.render(combined_text, True, sprite_color)
            text_surfaces.append((combined_surface, (debug_x, current_y)))
            current_y += line_height
            
            # Line 2: Chat/Action info (simplified)
            # Extract action type and name from chat
            if " : " in chat:
                action_parts = chat.split(" : ", 1)
                if len(action_parts) == 2:
                    action_type, action_name = action_parts
                    chat_text = f"{action_type} : {action_name}"
                else:
                    chat_text = chat
            else:
                chat_text = chat
            
            # Truncate if too long
            if len(chat_text) > 30:
                chat_text = chat_text[:27] + "..."
            
            chat_surface = self.font.render(chat_text, True, chat_color)
            text_surfaces.append((chat_surface, (debug_x, current_y)))
            current_y += line_height
            
            # Line 3: Direction
            dir_text = f"Dir: {direction}"
            dir_surface = self.font.render(dir_text, True, dir_color)
            text_surfaces.append((dir_surface, (debug_x, current_y)))
            current_y += line_height
            
            # Line 4: Position (without comma)
            pos_text = f"({int(pet_x)} {int(pet_y)})"
            pos_surface = self.font.render(pos_text, True, pos_color)
            text_surfaces.append((pos_surface, (debug_x, current_y)))
            current_y += line_height
            
            # Line 5: Position State (compact format)
            # Truncate if too long
            if len(position_state_text) > 30:
                position_state_text = position_state_text[:27] + "..."
            
            state_surface = self.font.render(position_state_text, True, state_color)
            text_surfaces.append((state_surface, (debug_x, current_y)))
            current_y += line_height
            
            # Line 6: Pinched State
            pinched_color = (255, 100, 100)  # Light red for pinched state
            pinched_text = f"Pinched: {pet.is_pinched_state()}"
            pinched_surface = self.font.render(pinched_text, True, pinched_color)
            text_surfaces.append((pinched_surface, (debug_x, current_y)))
            
            # Calculate background size
            if text_surfaces:
                max_width = max(surface.get_width() for surface, _ in text_surfaces)
                total_height = len(text_surfaces) * line_height + 20  # 20px padding
                
                # Draw black background with padding
                background_rect = pygame.Rect(debug_x - 10, debug_y - 10, max_width + 20, total_height)
                pygame.draw.rect(surface, background_color, background_rect)
                
                # Draw all text surfaces
                for text_surface, pos in text_surfaces:
                    surface.blit(text_surface, pos)
            
        except Exception as e:
            # Silently fail if rendering fails
            pass
    
    def should_show_boundaries(self):
        """Check if boundaries should be shown"""
        return self.debug_mode
    
    def should_show_selection_box(self):
        """Check if selection box should be shown"""
        return self.debug_mode 