import os
import sys
import glob
from pathlib import Path
from datetime import datetime
from loguru import logger

class LoggerConfig:
    """Loguru configuration for Desktop Pet Application with per-session logging"""
    
    def __init__(self):
        self.logs_dir = Path("logs")
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.logs_dir / f"{self.session_id}.log"
        self._setup_logger()
        self._cleanup_old_sessions()
    
    def _setup_logger(self):
        """Setup loguru logger with file and console handlers"""
        
        # Remove default logger
        logger.remove()
        
        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(exist_ok=True)
        
        # File handler - All levels with rotation per session
        logger.add(
            self.log_file,
            level="DEBUG",
            format="[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{level}] [{name}] {message}",
            rotation="10 MB",
            retention=5,  # Keep 5 files per session
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True
        )
        
        # Console handler - Only important levels (exclude DEBUG)
        logger.add(
            sys.stdout,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level>",
            colorize=True,
            backtrace=False,
            diagnose=False
        )
        
        # Error handler - Only ERROR and CRITICAL to stderr
        logger.add(
            sys.stderr,
            level="ERROR",
            format="<red>{time:HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    
    def _cleanup_old_sessions(self):
        """Clean up old log sessions, keeping only 3 most recent sessions"""
        try:
            # Get all log files in logs directory
            log_files = list(self.logs_dir.glob("*.log*"))
            
            if not log_files:
                return
            
            # Group files by session (base filename without rotation number)
            sessions = {}
            for log_file in log_files:
                # Extract base session name (e.g., "2024-01-15_14-30-25" from "2024-01-15_14-30-25.log.1")
                base_name = log_file.stem
                if base_name.endswith('.log'):
                    base_name = base_name[:-4]  # Remove .log suffix
                
                if base_name not in sessions:
                    sessions[base_name] = []
                sessions[base_name].append(log_file)
            
            # Sort sessions by creation time (newest first)
            session_times = []
            for session_name, files in sessions.items():
                # Use the main log file creation time as session time
                main_file = self.logs_dir / f"{session_name}.log"
                if main_file.exists():
                    session_times.append((session_name, main_file.stat().st_mtime))
                else:
                    # If main file doesn't exist, use the first file's time
                    session_times.append((session_name, files[0].stat().st_mtime))
            
            # Sort by creation time (newest first)
            session_times.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only 3 most recent sessions
            sessions_to_keep = set(session_name for session_name, _ in session_times[:3])
            
            # Delete old sessions
            deleted_count = 0
            for session_name, files in sessions.items():
                if session_name not in sessions_to_keep:
                    for file in files:
                        try:
                            file.unlink()
                            deleted_count += 1
                        except Exception as e:
                            # Log error but continue
                            print(f"Warning: Could not delete old log file {file}: {e}")
            
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} old log files, keeping 3 most recent sessions")
                
        except Exception as e:
            print(f"Warning: Could not cleanup old log sessions: {e}")
    
    def get_logger(self, name: str = None):
        """Get logger instance with module name"""
        if name:
            return logger.bind(name=name)
        return logger

# Global logger instance
log_config = LoggerConfig() 