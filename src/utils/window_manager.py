import os
import pygame

# Optional Win32 imports with fallback
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ Win32 modules not available. Using simple mode.")

class WindowManager:
    """Handles Win32 transparency, window setup, and monitor management"""
    
    @staticmethod
    def get_main_monitor_info():
        """Get main monitor dimensions and position"""
        if WIN32_AVAILABLE:
            return WindowManager._get_main_monitor_win32()
        else:
            return WindowManager._get_main_monitor_pygame()
    
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
            return WindowManager._get_main_monitor_pygame()
    
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
            return [WindowManager.get_main_monitor_info()]
        
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
            return [WindowManager.get_main_monitor_info()]
    
    @staticmethod
    def create_transparent_window(monitor_info=None, transparency_color=(255, 0, 255)):
        """Create transparent pygame window with dynamic color"""
        if not WIN32_AVAILABLE:
            raise ImportError("Win32 modules not available")
        
        # Get main monitor if not specified
        if monitor_info is None:
            monitor_info = WindowManager.get_main_monitor_info()
        
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
        WindowManager._apply_transparency(hwnd, transparency_color)
        
        # Ensure window is positioned correctly on the target monitor
        WindowManager._position_window_on_monitor(hwnd, monitor_info)
        
        print(f"✅ Transparent window created with color {transparency_color}")
        return display, hwnd, monitor_info['width'], monitor_info['height']
    
    @staticmethod
    def create_simple_window(monitor_info=None, width=800, height=600):
        """Create simple pygame window on specific monitor"""
        # Get main monitor if not specified
        if monitor_info is None:
            monitor_info = WindowManager.get_main_monitor_info()
        
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
    def _apply_transparency(hwnd, transparency_color=(255, 0, 255)):
        """Apply Win32 transparency settings with dynamic color"""
        try:
            # Set layered window
            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            new_style = current_style | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
            
            # Convert RGB to hex color
            r, g, b = transparency_color
            hex_color = (r << 16) | (g << 8) | b
            
            # Set color key transparency
            win32gui.SetLayeredWindowAttributes(
                hwnd, hex_color, 0, win32con.LWA_COLORKEY
            )
            
            # Always on top
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
        except Exception as e:
            print(f"⚠️ Could not apply transparency: {e}") 