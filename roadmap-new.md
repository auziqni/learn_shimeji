# Shimeji Desktop Pet - Unified Development Roadmap

## Project Overview

**Goal**: Create a desktop pet application similar to Shimeji with TikTok Live integration and window interaction capabilities.

**Target Platform**: Windows  
**Development Approach**: MVP (Minimum Viable Product) for each phase and step  
**Frame Rate**: 30 FPS  
**Sprite Size**: 128x128 px with transparency
**UI Strategy**: Pure Pygame with In-Game Control Panel

## Core Features

### Essential Features

- Desktop pet with various animations and behaviors
- Speech bubble system (text display for 10 seconds)
- TikTok Live integration for real-time chat interaction
- Multiple sprite support from DeviantArt format
- XML-based configuration system
- In-game control panel for settings and management
- Window interaction capabilities
- Transparent background with always-on-top functionality

### User Interactions

- **Left-click + Drag**: Move sprite
- **Double right-click**: Kill individual sprite
- **F1**: Toggle in-game control panel
- **Keyboard shortcuts**: Quick pet management
- **Right-click context menu**: Pet-specific actions

### TikTok Integration

- **Standalone Operation**: Application runs independently without TikTok
- **Optional Connection**: Username input through in-game control panel
- **Automatic Persistence**: Successful usernames saved to config.json
- **Error Handling**: Connection failures logged without breaking functionality
- **Real-time Response**: Chat messages trigger pet behaviors and speech bubbles

## Technical Stack

### Core Technologies

- **Python** with virtual environment
- **Pygame** for sprite rendering, animation, and UI
- **TikTokLive library** for chat integration
- **XML parsing** for sprite configurations
- **JSON** for settings storage
- **Windows API** for window interaction and transparency

### Dependencies

```python
pygame
TikTokLive  # https://github.com/isaackogan/TikTokLive
win32gui (pywin32)  # for window interaction and transparency
```

## File Structure

```
src/
├── main.py                 # Main application entry point
├── config.py              # Hardcoded settings and constants
├── animation/             # Animation system & management
│   ├── animation_manager.py    # MAESTRO - Central animation controller
│   ├── sprite_loader.py        # Sprite cache & memory management
│   ├── stay_animation.py       # Stay action type handler
│   ├── move_animation.py       # Move action type handler
│   ├── animate_animation.py    # Animate action type handler
│   ├── sequence_animation.py   # Sequence action type handler
│   └── behavior_processor.py   # Behavior logic & decision making
├── core/                  # Core business logic
│   ├── pet.py             # Individual pet entity
│   ├── environment.py     # Virtual boundary detection
│   └── interaction.py     # User input handling
├── ui/                    # In-game UI system
│   ├── ui_manager.py      # UI rendering and management
│   ├── control_panel.py   # In-game control panel
│   ├── speech_bubble.py   # Text bubble rendering
│   └── ui_components.py   # Reusable UI components
├── utils/                 # Data processing utilities
│   ├── xml_parser.py      # Legacy XML parsing
│   ├── xml2json.py        # XML to JSON conversion
│   ├── json_parser.py     # Modern JSON parsing
│   └── data_parser.py     # Data validation utilities
├── tiktok_integration.py  # TikTok Live connection and events
├── window_manager.py      # Window interaction and detection
├── assets/
│   ├── sprite_pack_1/
│   │   ├── conf/
│   │   │   ├── actions.xml
│   │   │   └── behaviors.xml
│   │   ├── shime1.png
│   │   ├── shime2.png
│   │   └── ...
│   └── sprite_pack_2/...
├── config.json           # User settings storage
└── README.md
```

## Sprite System

### DeviantArt Format Support

```
sprite_pack/
├── conf/
│   ├── actions.xml        # Animation definitions
│   └── behaviors.xml      # Behavior logic and conditions
├── shime1.png            # Sprite images
├── shime2.png
└── ...
```

### XML Structure Understanding

#### actions.xml Components

- **ActionList**: Animation definitions
- **Animation sequences**: Multiple Pose elements with timing
- **Pose attributes**:
  - `Image`: Sprite file path
  - `ImageAnchor`: Pivot point (e.g., "64,128")
  - `Velocity`: Movement speed
  - `Duration`: Frame duration
- **Action types**: Stay, Move, Animate, Sequence, Select
- **BorderType**: Floor, Wall, Ceiling (collision detection)

#### behaviors.xml Components

- **BehaviorList**: Behavior definitions with frequency
- **Conditions**: Desktop environment-based logic
- **NextBehaviorList**: Behavior chaining
- **Hidden behaviors**: Required system behaviors (Fall, Dragged, Thrown)
- **Frequency system**: Probability-based behavior selection

## Development Phases

### Phase 1: Foundation & Basic Interactions

#### Step 1: Core Infrastructure

**Goal**: Basic transparent window, sprite display, and user interactions

- [x] Project structure setup
- [ ] Pygame transparent window creation (always on top)
- [ ] Single sprite loading and display (shime1.png)
- [ ] Basic mouse event handling
- [ ] Left-click drag implementation
- [ ] Double right-click kill functionality
- [ ] Click-through technology for background interaction

**Deliverable**: Interactive sprite that can be moved and removed with transparent background

#### Step 2: In-Game Control Panel Foundation

**Goal**: Basic management interface within Pygame window

- [ ] In-game UI system with Pygame
- [ ] F1 key toggle for control panel
- [ ] Spawn new pet functionality
- [ ] Kill all pets functionality
- [ ] Basic settings UI structure (sliders, buttons, text input)
- [ ] JSON config save/load system
- [ ] Tab system for different settings

**Deliverable**: Working in-game control panel for pet management

#### Step 3: XML Parser & Animation System

**Goal**: Sprite animation and configuration

- [ ] XML parser for actions.xml and behaviors.xml
- [ ] Animation frame management system
- [ ] Basic animations (Stand, Walk, Sit) implementation
- [ ] Sprite positioning and anchor points
- [ ] Error handling for missing files
- [ ] Animation Manager (MAESTRO) implementation

**Deliverable**: Animated sprite with XML-driven behaviors

#### Step 4: Desktop Boundaries & Physics

**Goal**: Screen interaction and basic physics

- [ ] Screen boundary detection
- [ ] Gravity and floor collision system
- [ ] Basic state machine (idle, walking, sitting)
- [ ] Random behavior selection (simplified)
- [ ] Multi-pet management system (25+ pets support)

**Deliverable**: Pet that moves naturally within desktop bounds

### Phase 2: Advanced Features & Window Interaction

#### Step 1: Professional Logging System

**Goal**: Comprehensive logging and debugging

- [ ] Professional logging framework (time, type, content)
- [ ] Log levels: INFO, WARNING, ERROR
- [ ] Log panel integration in in-game control panel
- [ ] Log file output (.log format)
- [ ] Log filtering and search functionality

**Deliverable**: Complete logging system for debugging and monitoring

#### Step 2: Window Interaction System

**Goal**: Desktop window awareness and interaction

- [ ] Windows API integration (win32gui)
- [ ] Active window detection and boundaries
- [ ] Window state monitoring (minimized, maximized)
- [ ] Basic window positioning (sit on titlebar)
- [ ] Window edge detection and climbing

**Deliverable**: Pet that interacts with desktop windows

#### Step 3: Enhanced Behavior System

**Goal**: Rich behavior implementation

- [ ] Frequency-based behavior selection
- [ ] Simplified condition system
- [ ] Behavior chaining (NextBehaviorList)
- [ ] Random vs triggered behaviors
- [ ] Advanced window interactions (climb edges, jump between windows)

**Deliverable**: Sophisticated pet behavior system

#### Step 4: Speech Bubble System

**Goal**: Text communication system

- [ ] Speech bubble rendering system
- [ ] Text formatting and wrapping
- [ ] 10-second display timer
- [ ] Positioning relative to sprite
- [ ] Multiple bubble management

**Deliverable**: Pet communication system ready for TikTok integration

### Phase 3: TikTok Integration & Advanced Features

#### Step 1: TikTok Connection Infrastructure

**Goal**: Optional TikTok Live integration

- [ ] TikTokLive library integration
- [ ] Username input in in-game control panel
- [ ] Connection validation on-submit
- [ ] Config persistence for successful usernames
- [ ] Error handling with log-only feedback
- [ ] Standalone operation without TikTok

**Deliverable**: Optional TikTok Live connection system

#### Step 2: Chat Event Processing

**Goal**: Real-time chat interaction

- [ ] Chat message capture and parsing
- [ ] Command recognition system
- [ ] Behavior trigger from chat events
- [ ] User interaction response system
- [ ] Connection status monitoring and auto-reconnect

**Deliverable**: Real-time chat-to-behavior mapping

#### Step 3: Advanced Features

**Goal**: Audio, cloning, and polish

- [ ] Sound system implementation (.wav support)
- [ ] Volume control integration
- [ ] Clone/spawn system from behaviors
- [ ] Gift/donation reaction system
- [ ] Multi-pet coordination for chat events
- [ ] Performance optimization for multiple pets

**Deliverable**: Full-featured desktop pets with complete TikTok Live integration

## Technical Implementation Details

### State Management Structure

```python
pet_state = {
    "current_action": "idle",
    "position": {"x": 0, "y": 0},
    "direction": "right",  # for sprite flipping
    "is_dragging": False,
    "speech_bubble": {"text": "", "timer": 0},
    "health": 100,
    "active_window": None
}

ui_state = {
    "control_panel_visible": False,
    "active_tab": "pets",
    "focused_element": None,
    "dragging_slider": None
}
```

### Single-Threaded Architecture

- **Main Thread**: Pygame animation loop (30 FPS) + UI rendering
- **Background Thread**: TikTok Live listener (optional)
- **Background Thread**: Behavior timer/scheduler
- **Background Thread**: Window state monitoring

### Configuration System

```json
{
  "settings": {
    "volume": 70,
    "behavior_frequency": 50,
    "screen_boundaries": true,
    "auto_save": true
  },
  "tiktok": {
    "enabled": false,
    "last_successful_username": "",
    "auto_connect": false
  },
  "sprite_packs": ["assets/test_sprite"],
  "logging": {
    "level": "INFO",
    "save_to_file": true,
    "max_log_size": "10MB"
  },
  "active_pets": []
}
```

### Error Handling Requirements

- Missing sprite files
- Malformed XML configurations
- TikTok connection failures
- Windows API errors
- Audio system failures

## UI System Architecture

### In-Game UI Components

1. **Control Panel**
   - F1 toggle visibility
   - Tab system (Pets, Settings, TikTok, Logs)
   - Sliders, buttons, text input
   - Real-time updates

2. **Pet Management**
   - Spawn/Kill buttons
   - Pet list with individual controls
   - Clone functionality
   - Pet-specific settings

3. **Settings Panel**
   - Volume control
   - Behavior frequency
   - Screen boundaries
   - Auto-save options

4. **TikTok Panel**
   - Username input
   - Connect/Disconnect
   - Status display
   - Chat log

5. **Log Panel**
   - Real-time log display
   - Filter options
   - Search functionality
   - Export options

### UI Interaction Flow

```
Keyboard Event (F1) → Toggle Control Panel → Show/Hide UI
Mouse Click → UI Element Detection → Execute Action
Keyboard Input → Text Field Update → Save Settings
Tab Navigation → Switch Content → Update Display
```

## Testing Strategy

### Unit Testing

- XML parser validation
- Animation frame calculations
- Behavior probability system
- Window boundary detection
- UI component functionality

### Integration Testing

- Sprite loading with XML configs
- TikTok Live connection
- Multi-pet interaction
- In-game control panel functionality

### Performance Testing

- 30 FPS maintenance with multiple pets
- Memory usage optimization
- CPU usage monitoring
- Long-running stability
- UI responsiveness

## Documentation Requirements

### User Documentation

- Installation guide
- Basic usage instructions
- TikTok Live setup guide
- Sprite pack installation
- Troubleshooting guide

### Developer Documentation

- Code architecture overview
- XML configuration format
- Adding new behaviors
- Creating sprite packs
- API integration guide

## Future Considerations

### Potential Enhancements

- Multiple monitor support
- Custom sprite pack creator
- Advanced AI behavior
- Cloud sprite pack sharing
- Mobile companion app

### Scalability

- Plugin system architecture
- External behavior scripting
- Community sprite marketplace
- Advanced animation editor

## Success Metrics

### MVP Success Criteria

- Stable desktop pet with basic behaviors
- Working XML sprite loading system
- Functional in-game control panel
- Basic TikTok Live integration

### Full Success Criteria

- Rich window interaction system
- Robust multi-pet management (25+ pets)
- Seamless TikTok Live integration
- Community-friendly sprite format
- Performance optimization for multiple pets

## Key Changes from Original Roadmap

### 1. UI Strategy
- **Before**: PyQt5 control panel (separate window)
- **After**: Pure Pygame with in-game control panel
- **Reason**: Simpler architecture, better performance, unified experience

### 2. Threading Architecture
- **Before**: Complex multi-threaded Pygame + PyQt5
- **After**: Single-threaded Pygame with minimal background threads
- **Reason**: Easier to develop, debug, and maintain

### 3. File Structure
- **Before**: Separate GUI manager and control panel
- **After**: Integrated UI system within Pygame
- **Reason**: Better organization and reduced complexity

### 4. Dependencies
- **Before**: Pygame + PyQt5 + Windows API
- **After**: Pygame + Windows API (minimal dependencies)
- **Reason**: Reduced complexity and better performance

---

**Note**: This unified roadmap follows MVP principles - each step should produce a working, testable version before moving to the next step. Regular testing and user feedback should guide development priorities. 