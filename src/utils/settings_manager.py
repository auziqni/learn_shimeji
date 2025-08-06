import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

class SettingsManager:
    """
    Simplified settings management for Desktop Pet Application
    - Menyimpan, memuat, dan memvalidasi settings dari settings.json
    - API: get_setting, set_setting, save_settings, load_settings
    """
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.logger = logger.bind(name="settings_manager")
        self.settings = {}
        self.default_settings = self._get_default_settings()
        self.load_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings structure"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            
            "physics": {
                "gravity": 0.5,
                "friction": 0.95,
                "bounce_factor": 0.7,
                "max_velocity": 10.0
            },
            
            "boundaries": {
                "default_margin": 0.1,
                "safe_spawn_margin": 50,
                "wall_thickness": 10,
                "floor_thickness": 10,
                "floor_margin": 10,
                "wall_left_margin": 10,
                "wall_right_margin": 90,
                "ceiling_margin": 10
            },
            
            "ui": {
                "debug_mode": True,
                "show_boundaries": True,
                "show_fps": True,
                "control_panel_visible": False,
                "selected_pet_index": 0,
                "window_transparency": 255,
                "fps_target": 60,
                "info_font_size": 24,
                "debug_font_size": 18,
                "fps_update_interval": 500,
                "initial_pet_count": 3
            },
            
            "audio": {
                "enabled": True,
                "master_volume": 1.0,
                "sfx_volume": 0.7,
                "music_volume": 0.5,
                "mixer_settings": {
                    "frequency": 22050,
                    "size": -16,
                    "channels": 2,
                    "buffer": 512
                },
                "default_volume": 0.5,
                "frame_duration": 0.1
            },
            
            "logging": {
                "level": "INFO",
                "console_level": "INFO",
                "file_level": "DEBUG",
                "file_settings": {
                    "rotation_size": "10 MB",
                    "retention": 5,
                    "compression": "zip"
                },
                "session_cleanup": {
                    "max_sessions": 3
                },
                "formats": {
                    "file_format": "[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{level}] [{name}] {message}",
                    "console_format": "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level>",
                    "error_format": "<red>{time:HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level>"
                }
            },
            
            "sprites": {
                "default_sprite_pack": "Hornet",
                "default_action_type": "Stay",
                "cache_size": 100,
                "memory_limit_mb": 50,
                "preload_enabled": True,
                "preload_threshold": 0.8,
                "pixel_bytes": 4
            },
            
            "window": {
                "transparent_mode": True,
                "always_on_top": True,
                "click_through": False,
                "borderless": True,
                "resizable": False
            },
            
            "controls": {
                "movement_speed": 5.0,
                "key_repeat_delay": 100,
                "key_repeat_interval": 50
            },
            
            "performance": {
                "monitoring_enabled": True,
                "fps_threshold": 30,
                "frame_time_threshold": 33.33,
                "cpu_threshold": 80,
                "memory_threshold_mb": 500,
                "memory_growth_threshold": 50,
                "gc_threshold": 700,
                "gc_generation_threshold": 10,
                "gc_collection_threshold": 10,
                "auto_cleanup": True,
                "alert_history_size": 50,
                "monitoring_interval": 30,
                "memory_check_interval": 30
            },
            
            "tiktok": {
                "username": "",
                "enabled": False,
                "auto_connect": False,
                "connection_timeout": 30,
                "reconnect_interval": 60
            }
        }
    
    def load_settings(self) -> bool:
        """Load settings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to handle missing fields
                self.settings = self._merge_with_defaults(loaded_settings)
                self.logger.info(f"Settings loaded from {self.settings_file}")
                return True
            else:
                # Create default settings file
                self.settings = self.default_settings.copy()
                self.save_settings()
                self.logger.info(f"Created default settings file: {self.settings_file}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.settings = self.default_settings.copy()
            return False
    
    def save_settings(self) -> bool:
        """Save settings to JSON file"""
        try:
            # Update timestamp
            self.settings["last_updated"] = datetime.now().isoformat()
            
            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def _merge_with_defaults(self, loaded_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults to handle missing fields"""
        merged = self.default_settings.copy()
        
        def merge_dict(target: Dict, source: Dict):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value
        
        merge_dict(merged, loaded_settings)
        return merged
    
    def get_setting(self, path: str, default: Any = None) -> Any:
        """Get setting value by dot notation path (e.g., 'physics.gravity')"""
        try:
            keys = path.split('.')
            value = self.settings
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, path: str, value: Any) -> bool:
        """Set setting value by dot notation path"""
        try:
            keys = path.split('.')
            target = self.settings
            
            # Navigate to parent of target key
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Set the value
            target[keys[-1]] = value
            
            self.logger.debug(f"Setting updated: {path} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set setting {path}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def get_settings_section(self, section: str) -> Dict[str, Any]:
        """Get settings for a specific section"""
        return self.settings.get(section, {})
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.settings = self.default_settings.copy()
            success = self.save_settings()
            if success:
                self.logger.info("Settings reset to defaults")
            return success
        except Exception as e:
            self.logger.error(f"Failed to reset settings: {e}")
            return False 