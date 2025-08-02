# Sprint Documentation - Shimeji Desktop Pets Project

## 📋 Quick Reference

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Animation System** | Core animation management | `animation_manager.py`, `sprite_loader.py` |
| **Action Types** | Specific animation handlers | `stay_animation.py`, `move_animation.py`, etc. |
| **Core Logic** | Business logic & entities | `pet.py`, `environment.py`, `interaction.py` |
| **Data Processing** | File parsing & conversion | `json_parser.py`, `xml2json.py` |
| **Application** | Main entry point | `main.py` |

---

## 🏗️ Project Architecture

### **High-Level Flow:**
```
User Input → Main Application → Animation Manager → Behavior Processor → Action Animations → Rendering
```

### **Component Relationships:**
```
Animation Manager (MAESTRO)
    ↓
Behavior Processor → Action Type Animations
    ↓
Core Components (Pet, Environment, Interaction)
    ↓
Data Processing (JSON/XML Parsers)
```

---

## 📁 File Structure & Functions

### **Root Level**
```
src/
├── animation/           # Animation system & management
├── core/               # Core business logic
├── utils/              # Data processing utilities
└── main.py            # Application entry point
```

### **Animation System** (`src/animation/`)
```
animation/
├── animation_manager.py    # MAESTRO - Central animation controller
├── sprite_loader.py        # Sprite cache & memory management
├── stay_animation.py       # Stay action type handler
├── move_animation.py       # Move action type handler
├── animate_animation.py    # Animate action type handler
├── sequence_animation.py   # Sequence action type handler
└── behavior_processor.py   # Behavior logic & decision making
```

**Animation Manager (MAESTRO):**
- Central controller for all animation operations
- Manages multiple pets simultaneously
- Routes actions to appropriate animation handlers
- Handles memory optimization for 25+ pets
- Coordinates between behavior system and animation system

**Sprite Loader:**
- Global sprite cache management
- Memory-efficient loading for multiple pets
- Error handling for missing sprites
- Optimized for 25+ concurrent pets

**Action Type Animations:**
- **Stay Animation**: Static animations (no movement)
- **Move Animation**: Movement with velocity and boundary detection
- **Animate Animation**: Visual effects and sound integration
- **Sequence Animation**: Complex multi-action behaviors

**Behavior Processor:**
- AI-driven behavior decision making
- Environment-based behavior selection
- Behavior state management
- Action type determination

### **Core Logic** (`src/core/`)
```
core/
├── pet.py              # Individual pet entity
├── environment.py      # Virtual boundary detection
└── interaction.py      # User input handling
```

**Pet Entity:**
- Individual pet representation
- Position, animation state, behavior state management
- Update and render logic per pet
- Individual pet lifecycle management

**Environment:**
- Virtual wall, floor, ceiling detection
- Boundary validation and collision detection
- Screen boundary management
- Environment state tracking

**Interaction:**
- Mouse and keyboard input processing
- User interaction detection
- Click and hover event handling
- Input state management

### **Data Processing** (`src/utils/`)
```
utils/
├── xml_parser.py       # Legacy XML parsing
├── xml2json.py         # XML to JSON conversion
├── json_parser.py      # Modern JSON parsing
└── data_parser.py      # Data validation utilities
```

**XML Parser (Legacy):**
- Original XML file parsing
- Maintained for backward compatibility
- Will be replaced by JSON parser

**XML to JSON Converter:**
- Converts XML sprite data to JSON format
- Enables modern data processing
- Improves performance and maintainability

**JSON Parser (Modern):**
- Primary data parsing system
- Replaces XML parser for better performance
- Handles sprite pack data efficiently

**Data Parser:**
- Utility functions for data validation
- Common parsing operations
- Error handling and data sanitization

### **Application Entry** (`src/main.py`)
```
main.py                 # Main application with GUI logic
```

**Main Application:**
- Application entry point
- GUI management and screen handling
- Main game loop and event processing
- Application lifecycle management

---

## 🎯 MVP Goals & Features

### **Phase 1 - Foundation**
- Pet display and basic rendering
- Simple animation system (Stay, Move)
- Basic sprite loading and caching
- Individual pet entity management

### **Phase 2 - Core System**
- Behavior processing and decision making
- Environment boundary detection
- User interaction handling
- Animation switching and state management

### **Phase 3 - Advanced Features**
- Complex animations (Animate, Sequence)
- Advanced behavior patterns
- Enhanced user interactions
- Performance optimization

---

## 🔄 Data Flow Architecture

### **Animation System Flow:**
```
Behavior Decision → Animation Manager → Action Router → Specific Animation → Sprite Loader → Rendering
```

### **Pet Management Flow:**
```
User Input → Interaction Handler → Pet Entity → Animation Manager → Behavior Processor → Action Execution
```

### **Data Processing Flow:**
```
XML Files → JSON Converter → JSON Parser → Animation System → Runtime Execution
```

---

## 📊 Technical Specifications

### **Performance Targets:**
- Support 25+ concurrent pets
- 30 FPS target rendering
- Memory optimization for sprite caching
- Efficient animation switching

### **File Format Support:**
- **Input**: XML sprite pack files
- **Processing**: JSON converted data
- **Output**: Runtime animation execution

### **Action Type Distribution (Hornet Example):**
- **Stay Actions**: 10 (9.5%)
- **Move Actions**: 6 (5.7%)
- **Animate Actions**: 10 (9.5%)
- **Sequence Actions**: 58 (55.2%)
- **Embedded Actions**: 12 (11.4%) - Future implementation

---

## ⚠️ Important Notes

### **Required Dependencies:**
- Pygame for rendering and input handling
- JSON processing for data management
- XML processing for legacy support

### **Memory Management:**
- Global sprite cache for multiple pets
- Memory optimization for 25+ concurrent pets
- Efficient resource cleanup

### **Error Handling:**
- Graceful handling of missing sprites
- Fallback mechanisms for data parsing
- Robust animation state management

---

## 🔧 Development Guidelines

### **File Naming Convention:**
- Use descriptive names for animation files
- Follow Python naming conventions
- Maintain clear separation of concerns

### **Code Organization:**
- Keep animation logic separate from business logic
- Maintain clear interfaces between components
- Use consistent error handling patterns

### **Performance Considerations:**
- Optimize sprite loading and caching
- Minimize memory usage for multiple pets
- Efficient animation state management

---

## 📈 Future Roadmap

### **Short Term (MVP):**
- Complete basic animation system
- Implement core pet functionality
- Establish user interaction framework

### **Medium Term:**
- Advanced animation features
- Enhanced behavior system
- Performance optimizations

### **Long Term:**
- Embedded action support
- Advanced AI behavior patterns
- Extended sprite pack compatibility

---

*This documentation provides a comprehensive overview of the Shimeji desktop pets project architecture and development approach.* 