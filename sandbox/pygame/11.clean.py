import os
import pygame
import random
import sys

# Optional Win32 imports with fallback
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ Win32 modules not available. Using simple mode.")

# ========== MONITOR MANAGER (MULTI-MONITOR DETECTION) ==========
class MonitorManager:
    """Handles multi-monitor detection and main monitor positioning"""
    
    @staticmethod
    def get_main_monitor_info():
        """Get main monitor dimensions and position"""
        if WIN32_AVAILABLE:
            return MonitorManager._get_main_monitor_win32()
        else:
            return MonitorManager._get_main_monitor_pygame()
    
    @staticmethod
    def _get_main_monitor_win32():
        """Get main monitor info using Win32 API"""
        try:
            # Get primary monitor handle
            primary_monitor = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), \
                            win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # Get monitor info for primary display
            hdc = win32gui.GetDC(0)
            monitor_info = {
                'width': win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
                'height': win32api.GetSystemMetrics(win32con.SM_CYSCREEN),
                'x': 0,  # Primary monitor always starts at 0,0
                'y': 0,
                'is_primary': True
            }
            win32gui.ReleaseDC(0, hdc)
            
            print(f"🖥️ Main monitor: {monitor_info['width']}x{monitor_info['height']} at ({monitor_info['x']}, {monitor_info['y']})")
            return monitor_info
            
        except Exception as e:
            print(f"⚠️ Win32 monitor detection failed: {e}")
            return MonitorManager._get_main_monitor_pygame()
    
    @staticmethod
    def _get_main_monitor_pygame():
        """Fallback using pygame display info"""
        try:
            pygame.display.init()
            info = pygame.display.Info()
            monitor_info = {
                'width': info.current_w,
                'height': info.current_h,
                'x': 0,
                'y': 0,
                'is_primary': True
            }
            print(f"🖥️ Main monitor (pygame): {monitor_info['width']}x{monitor_info['height']}")
            return monitor_info
        except:
            # Ultimate fallback
            return {
                'width': 1920,
                'height': 1080,
                'x': 0,
                'y': 0,
                'is_primary': True
            }
    
    @staticmethod
    def get_all_monitors():
        """Get info for all monitors (Windows only)"""
        if not WIN32_AVAILABLE:
            return [MonitorManager.get_main_monitor_info()]
        
        monitors = []
        
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            try:
                monitor_info = win32api.GetMonitorInfo(hMonitor)
                monitor_rect = monitor_info['Monitor']
                work_rect = monitor_info['Work']
                
                monitor_data = {
                    'handle': hMonitor,
                    'width': monitor_rect[2] - monitor_rect[0],
                    'height': monitor_rect[3] - monitor_rect[1],
                    'x': monitor_rect[0],
                    'y': monitor_rect[1],
                    'is_primary': monitor_info['Flags'] & win32con.MONITORINFOF_PRIMARY != 0,
                    'work_area': {
                        'x': work_rect[0],
                        'y': work_rect[1],
                        'width': work_rect[2] - work_rect[0],
                        'height': work_rect[3] - work_rect[1]
                    }
                }
                monitors.append(monitor_data)
            except Exception as e:
                print(f"⚠️ Error getting monitor info: {e}")
            
            return True
        
        try:
            win32api.EnumDisplayMonitors(None, None, monitor_enum_proc, 0)
            if monitors:
                print(f"🖥️ Found {len(monitors)} monitor(s)")
                for i, mon in enumerate(monitors):
                    primary = " (PRIMARY)" if mon['is_primary'] else ""
                    print(f"   Monitor {i+1}: {mon['width']}x{mon['height']} at ({mon['x']}, {mon['y']}){primary}")
            return monitors
        except Exception as e:
            print(f"⚠️ Monitor enumeration failed: {e}")
            return [MonitorManager.get_main_monitor_info()]

# ========== PURE SPRITE CLASS (SINGLE RESPONSIBILITY) ==========
class Sprite:
    """Pure sprite - only handles image and position data"""
    
    def __init__(self, image_path, x=0, y=0):
        try:
            self.image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"⚠️ Could not load image {image_path}: {e}")
            # Create fallback red square
            self.image = pygame.Surface((64, 64))
            self.image.fill((255, 0, 0))
        
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def get_rect(self):
        """Get pygame rect for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def set_position(self, x, y):
        """Set sprite position"""
        self.x = x
        self.y = y
    
    def get_position(self):
        """Get sprite position"""
        return (self.x, self.y)
    
    def draw(self, surface):
        """Draw sprite to surface"""
        surface.blit(self.image, (self.x, self.y))

# ========== BOUNDARY MANAGER (SINGLE RESPONSIBILITY) ==========
class BoundaryManager:
    """Handles all boundary-related logic"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.boundaries = self._calculate_boundaries()
    
    def _calculate_boundaries(self):
        """Calculate boundary positions"""
        return {
            'left_wall': int(self.screen_width * 0.1),
            'right_wall': int(self.screen_width * 0.9),
            'ceiling': int(self.screen_height * 0.1),
            'floor': int(self.screen_height * 0.9)
        }
    
    def check_collision(self, sprite):
        """Check if sprite collides with boundaries"""
        rect = sprite.get_rect()
        collisions = {
            'left': rect.left < self.boundaries['left_wall'],
            'right': rect.right > self.boundaries['right_wall'],
            'top': rect.top < self.boundaries['ceiling'],
            'bottom': rect.bottom > self.boundaries['floor']
        }
        return collisions
    
    def clamp_position(self, sprite):
        """Clamp sprite position to boundaries"""
        x, y = sprite.get_position()
        
        # Clamp X
        if x < self.boundaries['left_wall']:
            x = self.boundaries['left_wall']
        elif x + sprite.width > self.boundaries['right_wall']:
            x = self.boundaries['right_wall'] - sprite.width
        
        # Clamp Y
        if y < self.boundaries['ceiling']:
            y = self.boundaries['ceiling']
        elif y + sprite.height > self.boundaries['floor']:
            y = self.boundaries['floor'] - sprite.height
        
        sprite.set_position(x, y)
    
    def get_safe_spawn_position(self, sprite_width, sprite_height):
        """Get random position within boundaries"""
        x = random.randint(
            self.boundaries['left_wall'] + 10,
            max(self.boundaries['left_wall'] + 11, self.boundaries['right_wall'] - sprite_width - 10)
        )
        y = random.randint(
            self.boundaries['ceiling'] + 10,
            max(self.boundaries['ceiling'] + 11, self.boundaries['floor'] - sprite_height - 10)
        )
        return (x, y)
    
    def draw_boundaries(self, surface):
        """Draw boundary lines"""
        # Left wall (blue)
        pygame.draw.line(surface, (0, 0, 255),
                        (self.boundaries['left_wall'], 0),
                        (self.boundaries['left_wall'], self.screen_height), 3)
        
        # Right wall (blue)
        pygame.draw.line(surface, (0, 0, 255),
                        (self.boundaries['right_wall'], 0),
                        (self.boundaries['right_wall'], self.screen_height), 3)
        
        # Ceiling (yellow)
        pygame.draw.line(surface, (255, 255, 0),
                        (0, self.boundaries['ceiling']),
                        (self.screen_width, self.boundaries['ceiling']), 3)
        
        # Floor (green)
        pygame.draw.line(surface, (0, 255, 0),
                        (0, self.boundaries['floor']),
                        (self.screen_width, self.boundaries['floor']), 3)

# ========== MOVEMENT CONTROLLER (SINGLE RESPONSIBILITY) ==========
class MovementController:
    """Handles movement input and position calculation"""
    
    def __init__(self, speed=2):
        self.speed = speed
    
    def get_movement_from_input(self, keys):
        """Calculate movement vector from keyboard input"""
        dx, dy = 0, 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        
        return (dx, dy)
    
    def apply_movement(self, sprite, dx, dy):
        """Apply movement to sprite"""
        current_x, current_y = sprite.get_position()
        new_x = current_x + dx
        new_y = current_y + dy
        sprite.set_position(new_x, new_y)

# ========== SPRITE MANAGER (SINGLE RESPONSIBILITY) ==========
class SpriteManager:
    """Manages collection of sprites"""
    
    def __init__(self):
        self.sprites = []
        self.selected_index = 0
    
    def add_sprite(self, sprite):
        """Add sprite to collection"""
        self.sprites.append(sprite)
        return len(self.sprites) - 1
    
    def remove_sprite(self, index):
        """Remove sprite by index"""
        if 0 <= index < len(self.sprites):
            self.sprites.pop(index)
            self._update_selection()
    
    def remove_selected_sprite(self):
        """Remove currently selected sprite"""
        if self.sprites:
            self.remove_sprite(self.selected_index)
    
    def get_selected_sprite(self):
        """Get currently selected sprite"""
        if self.sprites and 0 <= self.selected_index < len(self.sprites):
            return self.sprites[self.selected_index]
        return None
    
    def select_next(self):
        """Select next sprite"""
        if self.sprites:
            self.selected_index = (self.selected_index + 1) % len(self.sprites)
    
    def select_previous(self):
        """Select previous sprite"""
        if self.sprites:
            self.selected_index = (self.selected_index - 1) % len(self.sprites)
    
    def _update_selection(self):
        """Update selection after sprite removal"""
        if not self.sprites:
            self.selected_index = 0
        elif self.selected_index >= len(self.sprites):
            self.selected_index = len(self.sprites) - 1
    
    def get_sprite_count(self):
        """Get number of sprites"""
        return len(self.sprites)
    
    def draw_all(self, surface):
        """Draw all sprites"""
        for sprite in self.sprites:
            sprite.draw(surface)
    
    def draw_selection_indicator(self, surface):
        """Draw selection indicator around selected sprite"""
        selected = self.get_selected_sprite()
        if selected:
            rect = selected.get_rect()
            pygame.draw.rect(surface, (255, 255, 0), rect, 3)

# ========== WINDOW MANAGER WITH MONITOR AWARENESS ==========
class WindowManager:
    """Handles Win32 transparency and window setup with monitor awareness"""
    
    @staticmethod
    def create_transparent_window(monitor_info=None):
        """Create transparent pygame window on specific monitor"""
        if not WIN32_AVAILABLE:
            raise ImportError("Win32 modules not available")
        
        # Get main monitor if not specified
        if monitor_info is None:
            monitor_info = MonitorManager.get_main_monitor_info()
        
        # Set SDL position for specific monitor
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{monitor_info["x"]},{monitor_info["y"]}'
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        
        # Create pygame window
        display = pygame.display.set_mode(
            (monitor_info['width'], monitor_info['height']), 
            pygame.NOFRAME
        )
        pygame.display.set_caption("Desktop Pet - Main Monitor")
        
        # Get window handle and apply transparency
        hwnd = pygame.display.get_wm_info()["window"]
        WindowManager._apply_transparency(hwnd)
        
        # Ensure window is positioned correctly on the target monitor
        WindowManager._position_window_on_monitor(hwnd, monitor_info)
        
        print(f"✅ Transparent window created on main monitor: {monitor_info['width']}x{monitor_info['height']}")
        return display, hwnd, monitor_info['width'], monitor_info['height']
    
    @staticmethod
    def create_simple_window(monitor_info=None, width=800, height=600):
        """Create simple pygame window on specific monitor"""
        # Get main monitor if not specified
        if monitor_info is None:
            monitor_info = MonitorManager.get_main_monitor_info()
        
        # Calculate centered position on main monitor
        center_x = monitor_info['x'] + (monitor_info['width'] - width) // 2
        center_y = monitor_info['y'] + (monitor_info['height'] - height) // 2
        
        # Set window position
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{center_x},{center_y}'
        
        display = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Desktop Pet - Main Monitor (Simple)")
        
        print(f"✅ Simple window created on main monitor at ({center_x}, {center_y})")
        return display, None, width, height
    
    @staticmethod
    def _position_window_on_monitor(hwnd, monitor_info):
        """Ensure window is positioned correctly on target monitor"""
        try:
            win32gui.SetWindowPos(
                hwnd, 
                win32con.HWND_TOPMOST,
                monitor_info['x'], 
                monitor_info['y'],
                monitor_info['width'], 
                monitor_info['height'],
                win32con.SWP_SHOWWINDOW
            )
        except Exception as e:
            print(f"⚠️ Could not position window on monitor: {e}")
    
    @staticmethod
    def _apply_transparency(hwnd):
        """Apply Win32 transparency settings"""
        try:
            # Set layered window
            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_style = current_style | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
            
            # Set color key transparency (black = transparent)
            win32gui.SetLayeredWindowAttributes(
                hwnd, 0x000000, 0, win32con.LWA_COLORKEY
            )
            
            # Always on top
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
        except Exception as e:
            print(f"⚠️ Could not apply transparency: {e}")

# ========== ASSET MANAGER (SINGLE RESPONSIBILITY) ==========
class AssetManager:
    """Handles asset loading and fallback creation"""
    
    @staticmethod
    def get_sprite_path():
        """Get sprite image path with fallback"""
        # Try multiple possible paths
        possible_paths = [
            "shime1.png",
            "sprite.png",
            os.path.join("assets", "shime1.png"),
            os.path.join("sandbox", "mockSprite", "shime1.png"),
            os.path.join("..", "..", "sandbox", "mockSprite", "shime1.png")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found sprite: {path}")
                return path
        
        print("❌ No sprite image found, creating fallback...")
        return AssetManager._create_fallback_sprite()
    
    @staticmethod
    def _create_fallback_sprite():
        """Create fallback sprite if image not found"""
        print("💡 Creating fallback sprite...")
        fallback_surface = pygame.Surface((64, 64))
        fallback_surface.fill((255, 100, 100))  # Light red square
        
        # Add some pattern to make it more interesting
        pygame.draw.circle(fallback_surface, (255, 255, 255), (32, 32), 20)
        pygame.draw.circle(fallback_surface, (0, 0, 0), (25, 25), 5)  # Left eye
        pygame.draw.circle(fallback_surface, (0, 0, 0), (39, 25), 5)  # Right eye
        pygame.draw.arc(fallback_surface, (0, 0, 0), (20, 35, 24, 12), 0, 3.14, 2)  # Smile
        
        fallback_path = "fallback_sprite.png"
        pygame.image.save(fallback_surface, fallback_path)
        print(f"✅ Created: {fallback_path}")
        return fallback_path

# ========== MAIN APPLICATION WITH MONITOR DETECTION ==========
class DesktopPetApp:
    """Main application - orchestrates all systems with monitor awareness"""
    
    def __init__(self):
        self.running = False
        self.clock = None
        self.display = None
        self.show_boundaries = True
        self.transparent_mode = False
        self.monitor_info = None
        
        # Initialize systems
        self.sprite_manager = SpriteManager()
        self.movement_controller = MovementController(speed=3)
        self.boundary_manager = None
        
    def initialize(self):
        """Initialize application with main monitor detection"""
        try:
            print("🚀 Initializing Desktop Pet...")
            
            # Initialize pygame
            pygame.init()
            self.clock = pygame.time.Clock()
            
            # Detect monitors and get main monitor info
            self.monitor_info = MonitorManager.get_main_monitor_info()
            all_monitors = MonitorManager.get_all_monitors()
            
            if len(all_monitors) > 1:
                print(f"🖥️ Multi-monitor setup detected. Using main monitor only.")
            
            # Try transparent window first, fall back to simple
            try:
                if WIN32_AVAILABLE:
                    self.display, hwnd, screen_width, screen_height = WindowManager.create_transparent_window(self.monitor_info)
                    self.transparent_mode = True
                    print("✅ Transparent mode enabled on main monitor")
                else:
                    raise ImportError("Win32 not available")
            except Exception as e:
                print(f"⚠️ Transparent mode failed: {e}")
                print("🔄 Falling back to simple mode...")
                self.display, hwnd, screen_width, screen_height = WindowManager.create_simple_window(self.monitor_info)
                self.transparent_mode = False
                print("✅ Simple mode enabled on main monitor")
            
            # Initialize boundary manager
            self.boundary_manager = BoundaryManager(screen_width, screen_height)
            
            # Load assets and create initial sprites
            self._create_initial_sprites()
            
            print("✅ Application initialized successfully!")
            self._print_controls()
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_initial_sprites(self):
        """Create initial sprites"""
        image_path = AssetManager.get_sprite_path()
        
        for i in range(3):
            # Create sprite at safe position
            temp_sprite = Sprite(image_path, 0, 0)  # Temporary for size
            try:
                safe_x, safe_y = self.boundary_manager.get_safe_spawn_position(
                    temp_sprite.width, temp_sprite.height
                )
            except:
                # Fallback position if boundary calculation fails
                safe_x, safe_y = 100 + i * 80, 100 + i * 60
            
            # Create actual sprite at safe position
            sprite = Sprite(image_path, safe_x, safe_y)
            self.sprite_manager.add_sprite(sprite)
        
        print(f"✅ Created {self.sprite_manager.get_sprite_count()} sprites")
    
    def _print_controls(self):
        """Print control instructions"""
        print("\n🎮 Controls:")
        print("  WASD/Arrow Keys: Move selected sprite")
        print("  Q/E: Switch sprite selection")
        print("  SPACE: Add new sprite")
        print("  DELETE/X: Remove selected sprite")
        print("  B: Toggle boundaries visibility")
        print("  ESC: Exit")
        print(f"\n🎨 Mode: {'Transparent' if self.transparent_mode else 'Simple Window'}")
        if self.monitor_info:
            print(f"🖥️ Monitor: {self.monitor_info['width']}x{self.monitor_info['height']} (Main)")
        print("🎨 Boundaries:")
        print("  🔵 Blue: Walls | 🟡 Yellow: Ceiling | 🟢 Green: Floor")
        print("  🟡 Yellow Box: Selected sprite")
    
    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_q:
                    self.sprite_manager.select_previous()
                    print(f"Selected sprite #{self.sprite_manager.selected_index + 1}")
                
                elif event.key == pygame.K_e:
                    self.sprite_manager.select_next()
                    print(f"Selected sprite #{self.sprite_manager.selected_index + 1}")
                
                elif event.key == pygame.K_b:
                    self.show_boundaries = not self.show_boundaries
                    print(f"Boundaries: {'ON' if self.show_boundaries else 'OFF'}")
                
                elif event.key == pygame.K_SPACE:
                    self._add_new_sprite()
                
                elif event.key == pygame.K_DELETE or event.key == pygame.K_x:
                    self._remove_selected_sprite()
    
    def _add_new_sprite(self):
        """Add new sprite at safe position"""
        try:
            image_path = AssetManager.get_sprite_path()
            temp_sprite = Sprite(image_path, 0, 0)
            try:
                safe_x, safe_y = self.boundary_manager.get_safe_spawn_position(
                    temp_sprite.width, temp_sprite.height
                )
            except:
                # Fallback position
                safe_x, safe_y = random.randint(100, 400), random.randint(100, 300)
            
            new_sprite = Sprite(image_path, safe_x, safe_y)
            self.sprite_manager.add_sprite(new_sprite)
            print(f"➕ Added sprite #{self.sprite_manager.get_sprite_count()}")
        
        except Exception as e:
            print(f"❌ Error adding sprite: {e}")
    
    def _remove_selected_sprite(self):
        """Remove selected sprite"""
        if self.sprite_manager.get_sprite_count() > 1:  # Keep at least one sprite
            self.sprite_manager.remove_selected_sprite()
            print(f"➖ Removed sprite. Remaining: {self.sprite_manager.get_sprite_count()}")
        else:
            print("⚠️ Cannot remove last sprite!")
    
    def update(self):
        """Update game logic"""
        # Get movement input
        keys = pygame.key.get_pressed()
        dx, dy = self.movement_controller.get_movement_from_input(keys)
        
        # Apply movement to selected sprite
        if dx != 0 or dy != 0:
            selected = self.sprite_manager.get_selected_sprite()
            if selected:
                self.movement_controller.apply_movement(selected, dx, dy)
                if self.boundary_manager:
                    self.boundary_manager.clamp_position(selected)
    
    def render(self):
        """Render everything"""
        # Clear with black (transparent in transparent mode)
        if self.transparent_mode:
            self.display.fill((0, 0, 0))  # Black = transparent
        else:
            self.display.fill((50, 50, 50))  # Dark gray background
        
        # Draw boundaries if enabled
        if self.show_boundaries and self.boundary_manager:
            self.boundary_manager.draw_boundaries(self.display)
        
        # Draw all sprites
        self.sprite_manager.draw_all(self.display)
        
        # Draw selection indicator
        self.sprite_manager.draw_selection_indicator(self.display)
        
        # Draw info text (only in simple mode)
        if not self.transparent_mode:
            font = pygame.font.Font(None, 24)
            info_text = f"Sprite {self.sprite_manager.selected_index + 1}/{self.sprite_manager.get_sprite_count()}"
            text_surface = font.render(info_text, True, (255, 255, 255))
            self.display.blit(text_surface, (10, 10))
            
            # Show monitor info
            if self.monitor_info:
                monitor_text = f"Main Monitor: {self.monitor_info['width']}x{self.monitor_info['height']}"
                monitor_surface = font.render(monitor_text, True, (200, 200, 200))
                self.display.blit(monitor_surface, (10, 35))
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            print("❌ Failed to initialize. Exiting...")
            return
        
        print("🎮 Desktop Pet is running on main monitor! Use controls to interact.")
        self.running = True
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(60)  # 60 FPS
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("🏁 Desktop Pet closing...")
            pygame.quit()
            sys.exit()

# ========== ENTRY POINT ==========
def main():
    """Main entry point"""
    print("🌟 Starting Desktop Pet Application")
    print("📋 Dependencies check:")
    print(f"   - pygame: {'✅' if 'pygame' in sys.modules else '❌'}")
    print(f"   - win32: {'✅' if WIN32_AVAILABLE else '❌ (fallback to simple mode)'}")
    
    app = DesktopPetApp()
    app.run()

if __name__ == "__main__":
    main()