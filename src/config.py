# Configuration and constants for Desktop Pet Application

# Window and Display Settings
WINDOW_TITLE = "Desktop Pet - Main Monitor"
SIMPLE_WINDOW_TITLE = "Desktop Pet - Main Monitor (Simple)"
FALLBACK_RESOLUTION = (1920, 1080)
SIMPLE_WINDOW_SIZE = (800, 600)

# Sprite Settings
DEFAULT_SPRITE_SIZE = (64, 64)
FALLBACK_SPRITE_COLOR = (255, 0, 0)
FALLBACK_SPRITE_PATH = "fallback_sprite.png"

# Movement Settings
DEFAULT_MOVEMENT_SPEED = 3
DEFAULT_BOUNDARY_MARGIN = 0.1  # 10% of screen

# Debug Settings
DEFAULT_DEBUG_MODE = True
FPS_UPDATE_INTERVAL = 500  # milliseconds
FPS_TARGET = 60

# Asset Paths
POSSIBLE_SPRITE_PATHS = [
    "shime1.png",
    "sprite.png",
    "assets/shime1.png",
    "sandbox/mockSprite/shime1.png",
    "../sandbox/mockSprite/shime1.png"
]

# Boundary Colors
BOUNDARY_COLORS = {
    'left_wall': (0, 0, 255),    # Blue
    'right_wall': (0, 0, 255),   # Blue
    'ceiling': (255, 255, 0),    # Yellow
    'floor': (0, 255, 0)         # Green
}

# Selection Indicator
SELECTION_COLOR = (255, 255, 0)  # Yellow
SELECTION_THICKNESS = 3

# Debug Info Colors
DEBUG_TEXT_COLOR = (255, 255, 255)  # White
INFO_TEXT_COLOR = (255, 255, 255)   # White
MONITOR_INFO_COLOR = (200, 200, 200)  # Light gray

# Background Colors
TRANSPARENT_BG = (0, 0, 0)       # Black (transparent)
SIMPLE_BG = (50, 50, 50)         # Dark gray

# Font Settings
DEBUG_FONT_SIZE = 24
INFO_FONT_SIZE = 24

# Initial Sprite Count
INITIAL_SPRITE_COUNT = 3

# Safe Spawn Margins
SAFE_SPAWN_MARGIN = 10 