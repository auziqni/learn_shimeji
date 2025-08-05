"""
__init__.py - Control Panel Module
This module initializes the control panel tabs for the Shimeji TikTok application.
"""

# Import semua tab classes
from .general_settings_tab import GeneralSettingsTab
from .shimeji_settings_tab import ShimejiSettingsTab
from .tiktok_settings_tab import TiktokSettingsTab
from .shimeji_info_tab import ShimejiInfoTab


# Define what gets imported dengan "from tabs import *" 
__all__ = [
    "GeneralSettingsTab",
    "ShimejiSettingsTab",
    "TiktokSettingsTab",
    "ShimejiInfoTab"
]

# Package metadata
__version__ = "1.0.0"
__author__ = "auziqni"

# Package-level function (optional)
def get_tabs():
    """
    Returns a list of all control panel tabs.
    """
    return __all__