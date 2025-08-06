import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

class SettingsManager:
    """
    Centralized settings management for Desktop Pet Application
    - Menyimpan, memuat, dan memvalidasi settings dari settings.json
    - Validasi otomatis: tipe data, rentang nilai, default value injection
    - Logging warning/error jika ada field tidak valid
    - Fallback ke default jika tidak valid
    - API: get_setting, set_setting, validate_settings, reset_to_defaults, export_invalid_settings_report
    """
    # --- VALIDATION RULES ---
    VALIDATION_RULES = {
        "physics.gravity": {"type": float, "min": 0.0, "max": 2.0, "default": 0.5},
        "physics.friction": {"type": float, "min": 0.0, "max": 1.0, "default": 0.95},
        "physics.bounce_factor": {"type": float, "min": 0.0, "max": 1.0, "default": 0.7},
        "physics.max_velocity": {"type": float, "min": 1.0, "max": 100.0, "default": 10.0},
        "boundaries.default_margin": {"type": float, "min": 0.0, "max": 0.5, "default": 0.1},
        "boundaries.safe_spawn_margin": {"type": int, "min": 0, "max": 500, "default": 50},
        "ui.fps_target": {"type": int, "min": 1, "max": 240, "default": 60},
        "ui.info_font_size": {"type": int, "min": 8, "max": 64, "default": 24},
        "ui.debug_mode": {"type": bool, "default": True},
        "ui.debug_font_size": {"type": int, "min": 8, "max": 64, "default": 18},
        "ui.fps_update_interval": {"type": int, "min": 100, "max": 5000, "default": 500},
        "ui.initial_pet_count": {"type": int, "min": 1, "max": 10, "default": 3},
        # Tambahkan rules lain sesuai kebutuhan
    }

    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.logger = logger.bind(name="settings_manager")
        self.settings = {}
        self.default_settings = self._get_default_settings()
        self.backup_settings = {}
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
            
            "ui_components": {
                "default_colors": {
                    "background": [100, 100, 100],
                    "border": [150, 150, 150],
                    "text": [255, 255, 255],
                    "hover": [120, 120, 120],
                    "pressed": [80, 80, 80],
                    "disabled": [60, 60, 60]
                },
                "button_colors": {
                    "background": [70, 130, 180],
                    "hover": [100, 149, 237],
                    "pressed": [65, 105, 225]
                },
                "slider_colors": {
                    "background": [50, 50, 50],
                    "slider": [100, 149, 237],
                    "hover": [60, 60, 60]
                },
                "panel_colors": {
                    "background": [40, 40, 40],
                    "border": [100, 100, 100],
                    "title": [255, 255, 255]
                },
                "textbox_colors": {
                    "background": [60, 60, 60],
                    "text": [255, 255, 255],
                    "placeholder": [150, 150, 150],
                    "cursor": [255, 255, 255],
                    "border": [100, 100, 100]
                },
                "dimensions": {
                    "border_width": 2,
                    "corner_radius": 5,
                    "button_height": 35,
                    "slider_height": 20
                }
            },
            
            "control_panel": {
                "dimensions": {
                    "panel_width": 700,
                    "panel_height": 500,
                    "button_spacing": 120,
                    "button_height": 35
                },
                "fonts": {
                    "main_font_size": 28,
                    "small_font_size": 20,
                    "fallback_font": "arial"
                },
                "default_settings": {
                    "volume": 70,
                    "debug_mode": True,
                    "boundaries": True,
                    "auto_save": True
                }
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
            
            # Create backup before saving
            self._create_backup()
            
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
    
    def _create_backup(self):
        """Create backup of current settings"""
        if self.settings_file.exists():
            backup_file = self.settings_file.with_suffix('.backup')
            try:
                import shutil
                shutil.copy2(self.settings_file, backup_file)
                self.logger.debug(f"Settings backup created: {backup_file}")
            except Exception as e:
                self.logger.warning(f"Failed to create backup: {e}")
    
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
    
    def update_settings(self, new_settings: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        try:
            # Create backup of current settings
            self.backup_settings = self.settings.copy()
            
            # Merge new settings
            self.settings = self._merge_with_defaults(new_settings)
            
            # Save to file
            success = self.save_settings()
            
            if success:
                self.logger.info("Settings updated successfully")
            else:
                # Rollback on save failure
                self.settings = self.backup_settings
                self.logger.error("Settings update failed, rolled back")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update settings: {e}")
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous settings"""
        if self.backup_settings:
            self.settings = self.backup_settings.copy()
            success = self.save_settings()
            if success:
                self.logger.info("Settings rolled back successfully")
            return success
        return False
    
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
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def get_settings_section(self, section: str) -> Dict[str, Any]:
        """Get settings for a specific section"""
        return self.settings.get(section, {})
    
    def export_settings(self, export_path: str) -> bool:
        """Export settings to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Settings exported to {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str) -> bool:
        """Import settings from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate imported settings
            if not self._validate_imported_settings(imported_settings):
                self.logger.error("Imported settings validation failed")
                return False
            
            # Update settings
            success = self.update_settings(imported_settings)
            if success:
                self.logger.info(f"Settings imported from {import_path}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
    
    def _validate_imported_settings(self, settings: Dict[str, Any]) -> bool:
        """Basic validation of imported settings"""
        required_sections = [
            'physics', 'boundaries', 'ui', 'audio', 'logging', 
            'sprites', 'window', 'controls'
        ]
        
        for section in required_sections:
            if section not in settings:
                self.logger.warning(f"Missing required section: {section}")
                return False
        
        return True
    
    def get_settings_info(self) -> Dict[str, Any]:
        """Get information about current settings"""
        return {
            "file_path": str(self.settings_file),
            "file_exists": self.settings_file.exists(),
            "file_size": self.settings_file.stat().st_size if self.settings_file.exists() else 0,
            "last_updated": self.settings.get("last_updated", "Unknown"),
            "version": self.settings.get("version", "Unknown"),
            "total_settings": self._count_settings(self.settings)
        }
    
    def _count_settings(self, data: Any) -> int:
        """Count total number of settings"""
        if isinstance(data, dict):
            return sum(self._count_settings(value) for value in data.values())
        elif isinstance(data, list):
            return sum(self._count_settings(item) for item in data)
        else:
            return 1 

    def validate_settings(self, auto_fix=False) -> List[str]:
        """Validate all settings. If auto_fix=True, auto-correct invalid fields."""
        invalid_fields = []
        for key, rule in self.VALIDATION_RULES.items():
            value = self.get_setting(key, rule.get("default"))
            valid, fixed = self._validate_field(key, value)
            if not valid:
                invalid_fields.append((key, value, fixed))
                if auto_fix:
                    self.set_setting(key, fixed)
        if invalid_fields:
            self.logger.warning(f"Invalid settings found: {invalid_fields}")
        return invalid_fields

    def _validate_field(self, key: str, value: Any):
        """Return (is_valid, fixed_value) for a field based on VALIDATION_RULES"""
        rule = self.VALIDATION_RULES.get(key)
        if not rule:
            return True, value  # No rule, always valid
        expected_type = rule["type"]
        # Type check
        if expected_type == bool:
            if not isinstance(value, bool):
                return False, rule.get("default", False)
        elif expected_type == int:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except:
                    return False, rule.get("default", 0)
        elif expected_type == float:
            if not isinstance(value, (float, int)):
                try:
                    value = float(value)
                except:
                    return False, rule.get("default", 0.0)
        # Range check
        if "min" in rule and value < rule["min"]:
            return False, rule["default"]
        if "max" in rule and value > rule["max"]:
            return False, rule["default"]
        return True, value

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self._get_default_settings()
        self.save_settings()
        self.logger.info("Settings reset to defaults.")

    def export_invalid_settings_report(self, filename="invalid_settings_report.txt"):
        """Export a report of all invalid settings to a file."""
        invalids = self.validate_settings(auto_fix=False)
        if not invalids:
            self.logger.info("No invalid settings found.")
            return
        with open(filename, "w", encoding="utf-8") as f:
            for key, value, fixed in invalids:
                f.write(f"{key}: {value} (auto-fix: {fixed})\n")
        self.logger.info(f"Invalid settings report exported to {filename}") 