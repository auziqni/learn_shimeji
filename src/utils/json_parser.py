# JSON Parser for Desktop Pet Application
# This module will handle JSON parsing for settings and configurations

import json
import os

class JSONParser:
    """Modern JSON parsing utilities for settings and configurations"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def load_config(file_path):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return {}
    
    @staticmethod
    def save_config(file_path, data):
        """Save configuration to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")
            return False 