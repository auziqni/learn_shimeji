import os
import pygame
from utils.monitor_manager import MonitorManager

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