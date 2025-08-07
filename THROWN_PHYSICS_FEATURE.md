# 🚀 Thrown Physics Feature - Technical Specification

## 📋 **Overview**

Fitur **Thrown Physics** menambahkan kemampuan untuk melempar pet dengan physics yang natural dan realistic. Pet akan bergerak dalam parabola dengan gravity, bouncing, dan collision detection yang proper.

## 🎯 **Target Behavior**

### **User Interaction**
1. **Drag & Release**: User drag pet dan release dengan velocity tinggi
2. **Parabola Motion**: Pet bergerak dalam parabola natural
3. **Bouncing**: Pet bounce saat hit surface
4. **Recovery**: Pet kembali ke normal state setelah thrown

### **Physics Characteristics**
- **High Velocity**: Support velocity sampai 150+ pixels/frame
- **Parabola Trajectory**: Natural curve dengan gravity
- **Bouncing**: Realistic bounce dengan energy loss
- **Collision Detection**: Proper boundary handling

## 🔍 **Current State Analysis**

### **✅ What's Already Working**
- Basic physics engine di `environment.py`
- Velocity management system
- Boundary detection
- Basic collision handling

### **❌ Critical Gaps Identified**

#### **1. Physics Math Precision Issues**
```python
# CURRENT: Simple position-based velocity
dx = end_pos[0] - start_pos[0]
dy = end_pos[1] - start_pos[1]

# MISSING: Time-based velocity calculation
# Real velocity should be: distance/time
```

#### **2. State Management Complexity**
```python
# MISSING: State conflict handling
# What if pet is thrown while being dragged?
# What if user tries to drag a thrown pet mid-flight?
# How to handle multiple pets being thrown simultaneously?
```

#### **3. Integration Gaps**
```python
# MISSING: Animation manager integration
# How does thrown state affect current animations?
# How to transition between drag -> throw -> land animations?
# What if pet is mid-animation when thrown?
# DECISION: Thrown animation OVERRIDE semua animations (highest priority)
```

#### **4. Performance Issues**
```python
# MISSING: Performance optimization for multiple thrown pets
# No velocity capping for extreme throws
# No frame rate consideration for physics calculations
```

## 🛠️ **Technical Implementation**

### **📁 Files to Modify**

#### **1. `src/core/pet.py` - Add Thrown State Data**
```python
# Add these properties to Pet class
self.is_thrown = False
self.thrown_velocity = [0.0, 0.0]
self.thrown_timer = 0.0
self.thrown_angle = 0.0
self.thrown_power = 0.0
self.thrown_gravity = 0.5
self.drag_start_time = 0.0
self.drag_start_pos = [0, 0]
```

#### **2. `src/core/environment.py` - Enhanced Physics Engine**
```python
# Add these methods
def calculate_throw_velocity(self, start_pos, end_pos, drag_time):
    """Calculate realistic throw velocity with time precision"""
    
def apply_thrown_physics(self, pet, delta_time):
    """Apply specialized physics for thrown pets"""
    
def handle_thrown_collision(self, pet):
    """Handle collision detection for thrown pets"""
```

#### **3. `src/core/interaction.py` - Thrown Detection**
```python
# Add these methods (DECISION: Extend existing mouse interaction)
def detect_throw_gesture(self, pet, start_pos, end_pos, drag_time):
    """Detect if user gesture qualifies as throw"""
    
def initiate_throw(self, pet, velocity):
    """Initiate thrown state with given velocity"""
    
def handle_thrown_input(self, pet, event):
    """Handle input events for thrown pets"""
```

#### **4. `src/animation/animation_manager.py` - Animation Integration**
```python
# Add these methods
def handle_throw_transition(self, pet):
    """Handle animation transition for thrown pets"""
    
def save_animation_checkpoint(self, pet):
    """Save current animation state before throw"""
    
def restore_animation_checkpoint(self, pet):
    """Restore animation state after throw"""
```

#### **5. `src/utils/settings_manager.py` - Thrown Settings**
```python
# Add these settings
THROWN_PHYSICS = {
    'max_velocity': 150.0,
    'min_throw_velocity': 50.0,
    'throw_duration': 3.0,
    'bounce_energy_loss': 0.7,
    'gravity_multiplier': 1.5,
    'time_multiplier': 60.0,  # For frame-rate independent physics
    'fallback_multiplier': 2.0
}
```

### **🔧 Core Implementation Methods**

#### **1. Time-Based Velocity Calculation**
```python
def calculate_throw_velocity(self, start_pos, end_pos, drag_time):
    """Calculate realistic throw velocity with time precision"""
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    
    # Time-based velocity (critical for realism)
    if drag_time > 0:
        vx = dx / drag_time * self.settings.THROWN_PHYSICS['time_multiplier']
        vy = dy / drag_time * self.settings.THROWN_PHYSICS['time_multiplier']
    else:
        # Fallback for instant release
        vx = dx * self.settings.THROWN_PHYSICS['fallback_multiplier']
        vy = dy * self.settings.THROWN_PHYSICS['fallback_multiplier']
    
    # Apply physics constraints
    velocity_magnitude = math.sqrt(vx**2 + vy**2)
    max_velocity = self.settings.THROWN_PHYSICS['max_velocity']
    
    if velocity_magnitude > max_velocity:
        scale = max_velocity / velocity_magnitude
        vx *= scale
        vy *= scale
    
    return vx, vy
```

#### **2. State Management System**
```python
class ThrowStateManager:
    def __init__(self):
        self.thrown_pets = set()  # Track multiple thrown pets
        self.state_transitions = {
            'IDLE -> DRAGGING': True,
            'DRAGGING -> THROWN': True,
            'THROWN -> IDLE': True,
            'THROWN -> DRAGGING': False,  # Prevent mid-flight hijacking
            'THROWN -> THROWN': False,    # Prevent re-throwing
        }
    
    def can_transition(self, pet, from_state, to_state):
        """Check if state transition is allowed"""
        transition = f"{from_state} -> {to_state}"
        return self.state_transitions.get(transition, False)
    
    def add_thrown_pet(self, pet):
        """Add pet to thrown tracking"""
        self.thrown_pets.add(pet)
    
    def remove_thrown_pet(self, pet):
        """Remove pet from thrown tracking"""
        self.thrown_pets.discard(pet)
```

#### **3. Enhanced Physics Engine**
```python
def apply_thrown_physics(self, pet, delta_time):
    """Apply specialized physics for thrown pets"""
    if not pet.is_thrown:
        return
    
    # Update thrown timer
    pet.thrown_timer += delta_time
    
    # Apply gravity to thrown velocity
    pet.thrown_velocity[1] += pet.thrown_gravity * delta_time
    
    # Update position
    new_x = pet.x + pet.thrown_velocity[0] * delta_time
    new_y = pet.y + pet.thrown_velocity[1] * delta_time
    
    # Handle collision
    if self.check_thrown_collision(pet, new_x, new_y):
        self.handle_thrown_collision(pet)
    
    # Check if thrown state should end (DECISION: Timer < 3 OR hit boundary)
    if (pet.thrown_timer >= self.settings.THROWN_PHYSICS['throw_duration'] or 
        self.check_boundary_collision(pet, new_x, new_y)):
        self.end_thrown_state(pet)
```

#### **4. Animation Integration**
```python
def handle_throw_transition(self, pet):
    """Handle animation transition for thrown pets"""
    if pet.is_being_thrown():
        # Save current animation state
        self.save_animation_checkpoint(pet)
        
        # Switch to throw animation (DECISION: Thrown OVERRIDE semua)
        if self.has_action("Thrown"):
            self.set_action("Thrown")
        else:
            # Fallback to appropriate animation based on velocity
            if pet.thrown_velocity[1] > 0:  # Falling
                self.set_action("Fall") 
            else:  # Rising
                self.set_action("Jump")
    
def save_animation_checkpoint(self, pet):
    """Save current animation state before throw"""
    pet.animation_checkpoint = {
        'current_action': self.current_action,
        'frame_index': self.frame_index,
        'animation_timer': self.animation_timer
    }
```

### **🎯 Implementation Steps**

#### **Step 1: Add Thrown State Data to Pet Class**
- Add 7 new properties to Pet class
- Implement state management methods
- Add drag tracking properties

#### **Step 2: Enhance Physics Engine**
- Implement time-based velocity calculation
- Add thrown physics application
- Enhance collision detection for thrown pets

#### **Step 3: Implement Throw Detection**
- Add gesture detection for throw
- Implement velocity threshold checking
- Add state transition validation

#### **Step 4: Integrate with Animation System**
- Add animation checkpoint system
- Implement thrown animation transitions
- Handle animation state restoration

#### **Step 5: Add Settings and Configuration**
- Add thrown physics settings
- Implement performance optimizations
- Add error handling and validation

### **🔍 Testing Strategy**

#### **Unit Tests**
```python
def test_calculate_throw_velocity():
    """Test velocity calculation with various inputs"""
    
def test_throw_state_transitions():
    """Test state transition validation"""
    
def test_thrown_physics_application():
    """Test physics application for thrown pets"""
    
def test_animation_integration():
    """Test animation transitions during throw"""
```

#### **Integration Tests**
```python
def test_complete_throw_workflow():
    """Test complete drag -> throw -> land workflow"""
    
def test_multiple_thrown_pets():
    """Test multiple pets being thrown simultaneously"""
    
def test_throw_with_existing_animations():
    """Test throwing pet while it's animating"""
```

### **⚡ Performance Considerations**

#### **1. Velocity Capping**
```python
# Prevent extreme velocities that could cause performance issues
MAX_THROW_VELOCITY = 150.0
MIN_THROW_VELOCITY = 50.0
```

#### **2. Frame Rate Independence**
```python
# Use delta_time for physics calculations
velocity = distance / time * time_multiplier
```

#### **3. Thrown Pet Tracking**
```python
# Limit number of simultaneously thrown pets
MAX_THROWN_PETS = 5
```

### **🛡️ Error Handling**

#### **1. Invalid State Transitions**
```python
def validate_state_transition(self, pet, new_state):
    """Validate state transition before applying"""
    if not self.throw_manager.can_transition(pet.current_state, new_state):
        raise InvalidStateTransitionError(f"Cannot transition from {pet.current_state} to {new_state}")
```

#### **2. Physics Calculation Errors**
```python
def safe_velocity_calculation(self, start_pos, end_pos, drag_time):
    """Safe velocity calculation with error handling"""
    try:
        return self.calculate_throw_velocity(start_pos, end_pos, drag_time)
    except (ZeroDivisionError, ValueError) as e:
        logger.warning(f"Velocity calculation failed: {e}")
        return [0.0, 0.0]  # Safe fallback
```

#### **3. Animation Integration Errors**
```python
def safe_animation_transition(self, pet):
    """Safe animation transition with fallback"""
    try:
        self.handle_throw_transition(pet)
    except AnimationError as e:
        logger.warning(f"Animation transition failed: {e}")
        # Fallback to default animation
        self.set_default_animation(pet)
```

### **📊 Validation Criteria**

#### **✅ Success Metrics**
1. **Physics Realism**: Thrown pets follow natural parabola
2. **Performance**: No frame rate drops with multiple thrown pets
3. **State Management**: No state conflicts or invalid transitions
4. **Animation Integration**: Smooth transitions between animations
5. **Error Handling**: Graceful handling of edge cases

#### **❌ Failure Conditions**
1. **Physics Glitches**: Pets getting stuck or moving unnaturally
2. **Performance Issues**: Frame rate drops below 30 FPS
3. **State Conflicts**: Pets in invalid states
4. **Animation Bugs**: Broken or missing animations
5. **Memory Leaks**: Increasing memory usage over time

## 🚀 **Implementation Priority**

### **High Priority (Must Have)**
1. Time-based velocity calculation
2. State management system
3. Basic thrown physics application
4. Collision detection for thrown pets

### **Medium Priority (Should Have)**
1. Animation integration
2. Performance optimizations
3. Error handling
4. Settings configuration

### **Low Priority (Nice to Have)**
1. Advanced physics effects
2. Visual feedback improvements
3. Sound effects integration
4. Advanced animation sequences

## 📝 **Status**

**Status**: ✅ **READY FOR IMPLEMENTATION** - All Critical Decisions Made

**Key Decisions Made**:
1. ✅ **Mouse Interaction**: Extend existing mouse interaction system
2. ✅ **Animation Priority**: Thrown animation OVERRIDE semua (highest priority)
3. ✅ **Recovery Mechanism**: Timer < 3 seconds OR hit boundary (whichever first)

**Next Steps**:
1. Implement Step 1 (Add Thrown State Data)
2. Test velocity calculation with various inputs
3. Implement Step 2 (Enhanced Physics Engine)
4. Add comprehensive error handling
5. Perform integration testing

**Estimated Effort**: 2-3 days for complete implementation
**Risk Level**: Medium (requires careful state management)
**Dependencies**: None (uses existing systems) 