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