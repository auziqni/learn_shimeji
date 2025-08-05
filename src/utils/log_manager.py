from .logger import log_config
from loguru import logger
import time
import traceback

class LogManager:
    """Centralized logging manager for Desktop Pet Application"""
    
    def __init__(self, module_name: str = "main"):
        self.module_name = module_name
        self.logger = log_config.get_logger(module_name)
        self.start_time = time.time()
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, exc_info=None):
        """Log exception with traceback"""
        if exc_info is None:
            exc_info = traceback.format_exc()
        self.logger.error(f"{message}\n{exc_info}")
    
    def performance(self, operation: str, duration: float = None):
        """Log performance metrics"""
        if duration is None:
            duration = time.time() - self.start_time
        self.logger.info(f"Performance: {operation} took {duration:.3f}s")
    
    def user_action(self, action: str, details: str = ""):
        """Log user actions"""
        self.logger.info(f"User Action: {action} {details}".strip())
    
    def system_event(self, event: str, details: str = ""):
        """Log system events"""
        self.logger.info(f"System Event: {event} {details}".strip())
    
    def asset_event(self, asset_type: str, action: str, path: str = ""):
        """Log asset-related events"""
        self.logger.info(f"Asset {asset_type}: {action} {path}".strip())
    
    def pet_event(self, pet_id: int, action: str, details: str = ""):
        """Log pet-related events"""
        self.logger.info(f"Pet #{pet_id}: {action} {details}".strip())
    
    def ui_event(self, component: str, action: str, details: str = ""):
        """Log UI events"""
        self.logger.debug(f"UI {component}: {action} {details}".strip())
    
    def tiktok_event(self, event_type: str, details: str = ""):
        """Log TikTok integration events"""
        self.logger.info(f"TikTok {event_type}: {details}".strip())
    
    def monitor_event(self, event: str, details: str = ""):
        """Log monitor-related events"""
        self.logger.info(f"Monitor: {event} {details}".strip())
    
    def window_event(self, event: str, details: str = ""):
        """Log window-related events"""
        self.logger.debug(f"Window: {event} {details}".strip())

# Convenience function to get logger for any module
def get_logger(module_name: str = "main") -> LogManager:
    """Get logger instance for specific module"""
    return LogManager(module_name) 