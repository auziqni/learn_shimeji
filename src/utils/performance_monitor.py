import time
import threading
from typing import Dict, List, Optional
from collections import deque
from loguru import logger

# Optional psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available. CPU monitoring will be disabled.")

class PerformanceMonitor:
    """
    Minimal but effective performance monitoring
    - FPS tracking
    - Frame time analysis
    - CPU usage monitoring
    - Performance alerts
    """
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.logger = logger.bind(name="performance_monitor")
        
        # Frame timing
        self.frame_times = deque(maxlen=history_size)
        self.last_frame_time = time.time()
        
        # FPS tracking
        self.fps_history = deque(maxlen=history_size)
        self.current_fps = 0
        
        # CPU monitoring
        self.cpu_usage = 0
        self.cpu_history = deque(maxlen=history_size)
        
        # Performance thresholds
        self.fps_threshold = 30  # Alert if FPS drops below 30
        self.frame_time_threshold = 33.33  # Alert if frame time > 33.33ms (30 FPS)
        self.cpu_threshold = 80  # Alert if CPU usage > 80%
        
        # Alerts
        self.alerts = []
        self.alert_history = deque(maxlen=50)
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        
        self.logger.info("Performance monitor initialized")

    def start_frame(self):
        """Start timing a frame"""
        self.last_frame_time = time.time()

    def end_frame(self):
        """End timing a frame and record metrics"""
        current_time = time.time()
        frame_time = (current_time - self.last_frame_time) * 1000  # Convert to ms
        
        # Record frame time
        self.frame_times.append(frame_time)
        
        # Calculate FPS
        if frame_time > 0:
            self.current_fps = 1000 / frame_time
            self.fps_history.append(self.current_fps)
        
        # Check for performance issues
        self._check_performance_alerts(frame_time)

    def _check_performance_alerts(self, frame_time: float):
        """Check for performance issues and create alerts"""
        alerts = []
        
        # FPS alert
        if self.current_fps < self.fps_threshold:
            alerts.append(f"Low FPS: {self.current_fps:.1f} (threshold: {self.fps_threshold})")
        
        # Frame time alert
        if frame_time > self.frame_time_threshold:
            alerts.append(f"High frame time: {frame_time:.1f}ms (threshold: {self.frame_time_threshold}ms)")
        
        # CPU alert
        if self.cpu_usage > self.cpu_threshold:
            alerts.append(f"High CPU usage: {self.cpu_usage:.1f}% (threshold: {self.cpu_threshold}%)")
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"Performance alert: {alert}")
            self.alert_history.append({
                'time': time.time(),
                'message': alert,
                'fps': self.current_fps,
                'frame_time': frame_time,
                'cpu': self.cpu_usage
            })

    def start_monitoring(self):
        """Start background monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.logger.info("Performance monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Update CPU usage only if psutil is available
                if PSUTIL_AVAILABLE:
                    self.cpu_usage = psutil.cpu_percent(interval=1)
                    self.cpu_history.append(self.cpu_usage)
                else:
                    # Fallback: estimate CPU usage based on frame time
                    if self.frame_times:
                        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                        # Rough estimation: higher frame time = higher CPU usage
                        self.cpu_usage = min(100, max(0, (avg_frame_time / 16.67) * 50))  # 16.67ms = 60 FPS
                        self.cpu_history.append(self.cpu_usage)
                
                # Sleep to avoid excessive monitoring
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(5)

    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.frame_times:
            return {
                'fps': 0,
                'avg_fps': 0,
                'frame_time': 0,
                'avg_frame_time': 0,
                'cpu_usage': self.cpu_usage,
                'alerts': len(self.alert_history)
            }
        
        return {
            'fps': self.current_fps,
            'avg_fps': sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0,
            'frame_time': self.frame_times[-1] if self.frame_times else 0,
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times),
            'cpu_usage': self.cpu_usage,
            'alerts': len(self.alert_history),
            'min_fps': min(self.fps_history) if self.fps_history else 0,
            'max_fps': max(self.fps_history) if self.fps_history else 0
        }

    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """Get recent performance alerts"""
        return list(self.alert_history)[-count:]

    def clear_alerts(self):
        """Clear alert history"""
        self.alert_history.clear()
        self.logger.info("Performance alerts cleared")

    def set_thresholds(self, fps: Optional[int] = None, frame_time: Optional[float] = None, cpu: Optional[int] = None):
        """Set performance thresholds"""
        if fps is not None:
            self.fps_threshold = fps
        if frame_time is not None:
            self.frame_time_threshold = frame_time
        if cpu is not None:
            self.cpu_threshold = cpu
        
        self.logger.info(f"Performance thresholds updated: FPS={self.fps_threshold}, FrameTime={self.frame_time_threshold}ms, CPU={self.cpu_threshold}%")

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 