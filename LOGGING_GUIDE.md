# Logging System Guide

## Overview

The Desktop Pet Application now uses a robust **session-based logging system** built with **loguru** that provides:

- **Per-session log files** with timestamp naming (YYYY-MM-DD_HH-MM-SS.log)
- **Auto-cleanup** of old sessions (keeps 3 most recent sessions)
- **Rotation within sessions** (5 files per session, 10MB each)
- **Structured logging** with timestamps and module names
- **Multiple output destinations** (file + console)
- **Colored console output** for better readability
- **Specialized logging methods** for different event types

## File Structure

```
learn_shimeji/
├── logs/                                    # Log files directory
│   ├── 2024-01-15_14-30-25.log            # Current session (newest)
│   ├── 2024-01-15_14-30-25.log.1          # Rotation files for current session
│   ├── 2024-01-15_14-30-25.log.2          # (up to 5 files per session)
│   ├── 2024-01-15_14-25-10.log            # Previous session
│   ├── 2024-01-15_14-25-10.log.1          # Rotation files for previous session
│   ├── 2024-01-15_14-20-05.log            # Oldest kept session
│   └── ...
├── src/
│   ├── utils/
│   │   ├── logger.py                       # Loguru configuration
│   │   └── log_manager.py                  # Centralized logging manager
│   └── ...
```

## Session-Based Logging

### Session Definition
- **1 Run = 1 Session**: Each time you run `python main.py` creates a new session
- **Timestamp Naming**: Files named `YYYY-MM-DD_HH-MM-SS.log`
- **Auto-Cleanup**: Keeps only 3 most recent sessions (deletes older ones)

### Rotation Within Sessions
- **File Size**: 10MB per file
- **Retention**: 5 files per session maximum
- **Compression**: Old files are zipped
- **Example**: Session `2024-01-15_14-30-25` can have:
  - `2024-01-15_14-30-25.log` (main file)
  - `2024-01-15_14-30-25.log.1` (first rotation)
  - `2024-01-15_14-30-25.log.2` (second rotation)
  - `2024-01-15_14-30-25.log.3` (third rotation)
  - `2024-01-15_14-30-25.log.4` (fourth rotation)

### Auto-Cleanup Logic
- **On Startup**: Automatically deletes sessions older than 3 most recent
- **Maximum Files**: 15 files total (3 sessions × 5 files per session)
- **Safe Operation**: Continues even if cleanup fails

## Log Levels

### File Log (Session Files)
- **DEBUG**: Detailed technical information
- **INFO**: General application information
- **WARNING**: Issues that need attention
- **ERROR**: Errors that occurred
- **CRITICAL**: Fatal errors

### Console Output
- **INFO**: White text
- **WARNING**: Yellow text
- **ERROR**: Red text
- **CRITICAL**: Bold red text
- **DEBUG**: Hidden (file only)

## Usage

### Basic Logging

```python
from utils.log_manager import get_logger

# Get logger for your module
logger = get_logger("your_module_name")

# Basic logging
logger.debug("Debug message - file only")
logger.info("Info message - console + file")
logger.warning("Warning message - console + file")
logger.error("Error message - console + file")
logger.critical("Critical message - console + file")
```

### Specialized Logging Methods

```python
# User actions
logger.user_action("add_pet", "via keyboard shortcut")

# System events
logger.system_event("initialization", "completed successfully")

# Asset events
logger.asset_event("sprite", "loaded", "shime1.png")

# Pet events
logger.pet_event(1, "created", "at position (100, 100)")

# UI events
logger.ui_event("control_panel", "opened", "via F2 key")

# TikTok events
logger.tiktok_event("connection", "attempted for username: test")

# Monitor events
logger.monitor_event("detection", "found 2 monitors")

# Window events
logger.window_event("creation", "transparent window created")

# Performance metrics
logger.performance("sprite_loading", 0.123)

# Exception logging
try:
    # Some code that might fail
    pass
except Exception as e:
    logger.exception("Failed to load sprite")
```

## Log Format

### File Format
```
[2024-01-15 14:30:45.123] [INFO] [main] Application started successfully
[2024-01-15 14:30:45.124] [DEBUG] [asset_manager] Searching for sprite: shime1.png
[2024-01-15 14:30:45.125] [WARNING] [asset_manager] Sprite not found, creating fallback
```

### Console Format
```
14:30:45 | INFO     | main: Application started successfully
14:30:45 | WARNING  | asset_manager: Sprite not found, creating fallback
14:30:45 | ERROR    | pet: Could not load image shime1.png
```

## Configuration

### Session Management
- **Auto-Create Directory**: `logs/` directory created automatically
- **Session Naming**: `YYYY-MM-DD_HH-MM-SS.log` format
- **Cleanup**: Automatic on application startup
- **Retention**: 3 most recent sessions

### Rotation Settings
- **File Size**: 10MB per file
- **Files Per Session**: 5 maximum
- **Compression**: ZIP format for old files
- **Location**: `logs/` directory

### Console Output
- **Level**: INFO and above (excludes DEBUG)
- **Colors**: Enabled for better readability
- **Format**: Time | Level | Module: Message

## Best Practices

### 1. Module Naming
Use descriptive module names for better log organization:
```python
logger = get_logger("pet_manager")  # Good
logger = get_logger("pm")           # Avoid
```

### 2. Message Clarity
Write clear, actionable log messages:
```python
# Good
logger.info("Pet #1 moved to position (150, 200)")

# Avoid
logger.info("Moved")
```

### 3. Error Context
Always provide context for errors:
```python
try:
    sprite = pygame.image.load(path)
except pygame.error as e:
    logger.error(f"Failed to load sprite {path}: {e}")
```

### 4. Performance Logging
Use performance logging for slow operations:
```python
start_time = time.time()
# ... operation ...
logger.performance("sprite_loading", time.time() - start_time)
```

### 5. User Actions
Log all user interactions for debugging:
```python
logger.user_action("key_press", "SPACE key - add pet")
logger.user_action("mouse_click", "control panel button")
```

## Integration Examples

### In Main Application
```python
class DesktopPetApp:
    def __init__(self):
        self.logger = get_logger("main")
        self.logger.info("Initializing Desktop Pet Application")
    
    def initialize(self):
        try:
            # ... initialization code ...
            self.logger.info("Application initialized successfully")
        except Exception as e:
            self.logger.exception("Initialization failed")
```

### In Asset Manager
```python
class AssetManager:
    @staticmethod
    def get_sprite_path():
        logger = get_logger("asset_manager")
        
        for path in config.POSSIBLE_SPRITE_PATHS:
            if os.path.exists(path):
                logger.asset_event("sprite", "found", path)
                return path
        
        logger.warning("No sprite image found, creating fallback")
        return AssetManager._create_fallback_sprite()
```

### In Pet Management
```python
class PetManager:
    def __init__(self):
        self.logger = get_logger("pet_manager")
    
    def add_pet(self, pet):
        self.pets.append(pet)
        self.logger.pet_event(len(self.pets), "added", f"total pets: {len(self.pets)}")
```

## Session Management

### Understanding Sessions
- **Session = 1 Application Run**: Each time you start the app
- **Unique Timestamp**: Each session gets a unique timestamp
- **Isolated Logs**: Each session's logs are separate from others

### Example Session Lifecycle
```
1. Run 1: 2024-01-15_14-30-25.log (Session A)
2. Run 2: 2024-01-15_14-35-10.log (Session B)
3. Run 3: 2024-01-15_14-40-15.log (Session C)
4. Run 4: 2024-01-15_14-45-20.log (Session D) → Session A deleted
```

### Benefits of Session-Based Logging
- **Easy Debugging**: Each run has its own log file
- **No Log Mixing**: Clear separation between different runs
- **Automatic Cleanup**: Old sessions don't accumulate
- **Better Organization**: Timestamp makes it easy to find specific runs

## Troubleshooting

### Log File Not Created
- Check if `logs/` directory exists (auto-created)
- Verify write permissions
- Check for disk space

### Console Output Missing
- Ensure log level is INFO or above
- Check if stderr is redirected
- Verify terminal supports colors

### Performance Issues
- DEBUG level logs are file-only to reduce console overhead
- Log rotation prevents unlimited file growth
- Async logging prevents blocking

### Session Cleanup Issues
- Check file permissions in `logs/` directory
- Verify no files are locked by other processes
- Check available disk space

## Migration from print()

Replace print statements with appropriate logging:

```python
# Before
print("✅ Application started")
print(f"⚠️ Warning: {message}")
print(f"❌ Error: {error}")

# After
logger.info("Application started")
logger.warning(f"Warning: {message}")
logger.error(f"Error: {error}")
```

## Testing the Logging System

### Test Script
Use the provided test scripts:
```bash
# Test basic logging
python test_logging.py

# Test session-based logging
python test_session_logging.py
```

### Manual Testing
1. Run the application multiple times
2. Check `logs/` directory for new session files
3. Verify old sessions are cleaned up
4. Check log rotation within sessions

## Future Enhancements

- **Log filtering** by module or level
- **Log search** functionality
- **Log export** to different formats
- **Real-time log monitoring**
- **Log analytics** and statistics
- **Session comparison** tools
- **Log visualization** dashboard 