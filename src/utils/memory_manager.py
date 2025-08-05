import gc
import threading
import time
from typing import Dict, List, Optional, Callable
from collections import deque
from loguru import logger

# Optional psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available. Memory monitoring will be limited.")

class MemoryManager:
    """
    Minimal but effective memory management
    - Memory leak detection
    - Garbage collection optimization
    - Memory profiling
    - Automatic memory cleanup
    """
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.logger = logger.bind(name="memory_manager")
        
        # Memory tracking
        self.memory_history = deque(maxlen=100)
        if PSUTIL_AVAILABLE:
            self.initial_memory = psutil.Process().memory_info().rss
        else:
            self.initial_memory = 0  # Will be estimated
        self.last_memory_check = time.time()
        
        # Memory thresholds
        self.memory_threshold_mb = 500  # Alert if memory usage > 500MB
        self.memory_growth_threshold = 50  # Alert if memory growth > 50MB in 5 minutes
        
        # Leak detection
        self.memory_growth_rate = 0
        self.leak_suspicion_count = 0
        self.max_leak_suspicions = 3
        
        # Garbage collection
        self.gc_stats = {
            'collections': 0,
            'objects_freed': 0,
            'last_collection_time': 0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.cleanup_callbacks = []
        
        self.logger.info("Memory manager initialized")

    def start_monitoring(self):
        """Start background memory monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop background memory monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.logger.info("Memory monitoring stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._check_memory_usage()
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(10)

    def _check_memory_usage(self):
        """Check current memory usage and detect issues"""
        if PSUTIL_AVAILABLE:
            current_memory = psutil.Process().memory_info().rss
            memory_mb = current_memory / (1024 * 1024)
        else:
            # Fallback: estimate memory usage based on object count
            object_count = len(gc.get_objects())
            memory_mb = object_count * 0.001  # Rough estimation: 1KB per object
            current_memory = memory_mb * 1024 * 1024
        
        # Record memory usage
        self.memory_history.append({
            'time': time.time(),
            'memory_mb': memory_mb,
            'memory_bytes': current_memory
        })
        
        # Check memory threshold
        if memory_mb > self.memory_threshold_mb:
            self.logger.warning(f"High memory usage: {memory_mb:.1f}MB (threshold: {self.memory_threshold_mb}MB)")
        
        # Check memory growth
        if len(self.memory_history) >= 2:
            recent_memory = self.memory_history[-1]['memory_mb']
            older_memory = self.memory_history[0]['memory_mb']
            growth = recent_memory - older_memory
            
            if growth > self.memory_growth_threshold:
                self.leak_suspicion_count += 1
                self.logger.warning(f"Memory growth detected: {growth:.1f}MB in {self.check_interval}s")
                
                if self.leak_suspicion_count >= self.max_leak_suspicions:
                    self.logger.error("Potential memory leak detected! Triggering cleanup...")
                    self._trigger_cleanup()
                    self.leak_suspicion_count = 0

    def _trigger_cleanup(self):
        """Trigger memory cleanup"""
        self.logger.info("Starting memory cleanup...")
        
        # Run garbage collection
        self.force_garbage_collection()
        
        # Run custom cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Cleanup callback error: {e}")
        
        self.logger.info("Memory cleanup completed")

    def force_garbage_collection(self):
        """Force garbage collection and record stats"""
        before_objects = len(gc.get_objects())
        
        # Run garbage collection
        collected = gc.collect()
        
        after_objects = len(gc.get_objects())
        objects_freed = before_objects - after_objects
        
        # Update stats
        self.gc_stats['collections'] += 1
        self.gc_stats['objects_freed'] += objects_freed
        self.gc_stats['last_collection_time'] = time.time()
        
        self.logger.info(f"Garbage collection: {collected} objects collected, {objects_freed} objects freed")
        
        return collected, objects_freed

    def add_cleanup_callback(self, callback: Callable):
        """Add custom cleanup callback"""
        self.cleanup_callbacks.append(callback)
        self.logger.debug(f"Added cleanup callback: {callback.__name__}")

    def remove_cleanup_callback(self, callback: Callable):
        """Remove cleanup callback"""
        if callback in self.cleanup_callbacks:
            self.cleanup_callbacks.remove(callback)
            self.logger.debug(f"Removed cleanup callback: {callback.__name__}")

    def get_memory_stats(self) -> Dict:
        """Get current memory statistics"""
        if PSUTIL_AVAILABLE:
            current_memory = psutil.Process().memory_info().rss
            memory_mb = current_memory / (1024 * 1024)
        else:
            # Fallback: estimate memory usage
            object_count = len(gc.get_objects())
            memory_mb = object_count * 0.001  # Rough estimation
            current_memory = memory_mb * 1024 * 1024
        
        # Calculate memory growth
        memory_growth = 0
        if len(self.memory_history) >= 2:
            recent_memory = self.memory_history[-1]['memory_mb']
            older_memory = self.memory_history[0]['memory_mb']
            memory_growth = recent_memory - older_memory
        
        return {
            'current_memory_mb': memory_mb,
            'initial_memory_mb': self.initial_memory / (1024 * 1024) if self.initial_memory > 0 else 0,
            'memory_growth_mb': memory_growth,
            'memory_history_count': len(self.memory_history),
            'leak_suspicion_count': self.leak_suspicion_count,
            'gc_collections': self.gc_stats['collections'],
            'gc_objects_freed': self.gc_stats['objects_freed'],
            'last_gc_time': self.gc_stats['last_collection_time'],
            'cleanup_callbacks': len(self.cleanup_callbacks),
            'psutil_available': PSUTIL_AVAILABLE
        }

    def get_memory_history(self, count: int = 20) -> List[Dict]:
        """Get recent memory history"""
        return list(self.memory_history)[-count:]

    def set_thresholds(self, memory_threshold_mb: Optional[int] = None, growth_threshold: Optional[int] = None):
        """Set memory thresholds"""
        if memory_threshold_mb is not None:
            self.memory_threshold_mb = memory_threshold_mb
        if growth_threshold is not None:
            self.memory_growth_threshold = growth_threshold
        
        self.logger.info(f"Memory thresholds updated: Memory={self.memory_threshold_mb}MB, Growth={self.memory_growth_threshold}MB")

    def clear_memory_history(self):
        """Clear memory history"""
        self.memory_history.clear()
        self.leak_suspicion_count = 0
        self.logger.info("Memory history cleared")

    def optimize_garbage_collection(self):
        """Optimize garbage collection settings"""
        # Set garbage collection thresholds
        gc.set_threshold(700, 10, 10)  # More aggressive collection
        self.logger.info("Garbage collection optimized")

# Global memory manager instance
memory_manager = MemoryManager() 