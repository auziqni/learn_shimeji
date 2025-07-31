# 🚀 Teknisee Shimeji TikTok - Step-by-Step Development Guide

## 📋 **Current Status**

- ✅ **Project structure** defined
- ✅ **xml_parser.py** implemented (excellent!)
- ✅ **control_panel.py** basic structure ready
- 🔄 **Animation system** - ready to implement

---

## 🎯 **Phase 1: Animation System Implementation**

### **Step 1.1: Create `animation.py`** ⚡ **(CURRENT FOCUS)**

**Goal:** Core frame rendering and timing logic

**Files to create:**

```
src/animation.py
```

**Key Components:**

```python
class AnimationFrame:
    # Single frame data structure

class Animation:
    # Single animation sequence management
    # Frame timing and transitions
    # Play/pause/stop controls
    # Sprite loading with internal caching
```

**Testing:**

- Load single sprite pack
- Display frame sequence with proper timing
- Test loop functionality

**Success Criteria:**

- Can load PNG sprites from assets/
- Proper frame timing (30 FPS base)
- Memory efficient sprite caching

---

### **Step 1.2: Create `animation_manager.py`**

**Goal:** Coordinate multiple animations for sprite pack

**Files to create:**

```
src/animation_manager.py
```

**Key Components:**

```python
class AnimationManager:
    # Manage all animations for one sprite pack
    # Integration with xml_parser
    # Animation switching logic
    # Facing direction management
```

**Integration Points:**

- Import and use `animation.py`
- Import and use `utils/xml_parser.py`
- Handle sprite pack loading

**Testing:**

- Load all animations from XML
- Switch between animations ("Walk" → "Sit")
- Test with existing XML data

**Success Criteria:**

- All XML actions loaded as Animation objects
- Smooth animation switching
- Proper integration with xml_parser

---

### **Step 1.3: Animation System Integration Test**

**Goal:** Verify complete animation pipeline

**Test Script:**

```python
# test_animation_system.py
import pygame
from utils.xml_parser import XMLParser
from animation_manager import AnimationManager

# Initialize
pygame.init()
screen = pygame.display.set_mode((800, 600))
xml_parser = XMLParser()
anim_manager = AnimationManager("Hornet", xml_parser)

# Test animation switching
anim_manager.play("Walk")
# Game loop test
```

**Success Criteria:**

- Animations render properly
- No performance issues with 25+ pets simulation
- Clean error handling for missing sprites

---

## 🐾 **Phase 2: Pet Behavior System**

### **Step 2.1: Create `desktop_pet.py`**

**Goal:** Individual pet logic and behavior

**Files to create:**

```
src/desktop_pet.py
```

**Key Components:**

```python
class DesktopPet:
    # Pet state management (position, stats)
    # Medium complexity AI behavior
    # Mouse interaction handling
    # Physics simulation (gravity, bouncing)
    # Animation integration
```

**Integration Points:**

- Use `animation_manager.py` for animations
- Handle user input events
- Manage pet lifecycle

**Testing:**

- Single pet on screen
- Basic AI behavior (walk, sit, idle)
- Mouse drag and drop
- Animation triggers from behavior

---

### **Step 2.2: Pet Behavior Testing**

**Goal:** Verify pet AI and interactions

**Test Cases:**

- Pet spawns and starts with idle animation
- Pet randomly switches to walk/sit behaviors
- Mouse drag moves pet smoothly
- Pet responds to clicks appropriately
- Multiple pets don't interfere with each other

---

## 🎮 **Phase 3: GUI Management System**

### **Step 3.1: Create `gui_manager.py`**

**Goal:** Pygame window and rendering coordination

**Files to create:**

```
src/gui_manager.py
```

**Key Components:**

```python
class GUIManager:
    # Pygame window management
    # Transparent, always-on-top window
    # Main game loop (30 FPS)
    # Event handling and dispatching
    # Multiple pets coordination
```

**Integration Points:**

- Manage collection of `DesktopPet` instances
- Handle pygame window setup
- Coordinate rendering pipeline
- Event distribution system

**Testing:**

- Transparent window appears correctly
- Multiple pets render simultaneously
- Mouse events reach correct pets
- Smooth 30 FPS performance

---

### **Step 3.2: Multi-Pet System Test**

**Goal:** Verify 25+ pets performance

**Test Scenarios:**

- Spawn 25 pets simultaneously
- Monitor FPS and memory usage
- Test mouse interaction with overlapping pets
- Verify animation sync and independence

---

## ⚙️ **Phase 4: Configuration & Control Integration**

### **Step 4.1: Create `config.py`**

**Goal:** Centralized configuration management

**Files to create:**

```
src/config.py
```

**Key Components:**

```python
class ConfigManager:
    # JSON file operations
    # Settings validation
    # Default values handling
    # Configuration access API
```

**Integration Points:**

- Used by all modules for settings
- Connected to control_panel for UI
- Persistent storage in config.json

---

### **Step 4.2: Update `control_panel.py`**

**Goal:** Connect UI to pet management

**Updates:**

- Integrate with `gui_manager.py` for pet spawning
- Connect settings to `config.py`
- Add real functionality to placeholder tabs

**Testing:**

- Control panel can spawn pets
- Settings persist between sessions
- UI reflects current application state

---

### **Step 4.3: Complete Integration Test**

**Goal:** Full desktop pet application

**Test Cases:**

- Launch application → control panel appears
- Spawn pets via control panel → pets appear on desktop
- Change settings → pets behavior updates
- Close/reopen → settings and pets restored
- All mouse interactions work properly

---

## 🎵 **Phase 5: TikTok Integration** (Future)

### **Step 5.1: TikTok Live Connection**

**Files to create:**

```
src/tiktok_integration.py
```

**Key Features:**

- TikTok Live chat connection
- Chat message parsing
- Command recognition system

---

### **Step 5.2: Pet Response System**

**Integration:**

- Connect TikTok messages to pet behaviors
- Speech bubble system
- Special animations for donations/follows

---

### **Step 5.3: Complete TikTok Feature**

**Final Testing:**

- Live chat triggers pet actions
- Multiple pets respond to commands
- Stable connection handling

---

## 🧪 **Testing Strategy per Phase**

### **Unit Testing (Each Step):**

- Create simple test script for each component
- Verify core functionality works
- Check error handling
- Performance validation

### **Integration Testing (Each Phase):**

- Test component interactions
- Verify data flow between modules
- Check for memory leaks
- Performance under load

### **System Testing (Phase 4):**

- Complete user scenarios
- Multi-pet performance testing
- UI/UX validation
- Configuration persistence

---

## 📊 **Success Metrics**

### **Phase 1 Success:**

- ✅ Animations load and play smoothly
- ✅ 30 FPS performance maintained
- ✅ Memory usage under 100MB for 25 pets

### **Phase 2 Success:**

- ✅ Pets exhibit believable behavior
- ✅ Mouse interactions feel responsive
- ✅ No crashes or freezes during gameplay

### **Phase 3 Success:**

- ✅ Transparent window works on desktop
- ✅ 25+ pets render simultaneously
- ✅ Event handling works correctly

### **Phase 4 Success:**

- ✅ Complete desktop pet application
- ✅ Settings persistence works
- ✅ Control panel fully functional

### **Phase 5 Success:**

- ✅ TikTok Live integration working
- ✅ Pets respond to chat commands
- ✅ Stable for extended streaming sessions

---

## 🎯 **Current Action Item**

**NEXT:** Implement `src/animation.py`

- Focus on AnimationFrame and Animation classes
- Implement sprite loading with caching
- Create frame timing system
- Test with existing Hornet sprite pack

**Ready to start coding Phase 1, Step 1.1!** 🚀
