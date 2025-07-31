# XML Parser Update - Smart Sprite Support

## 🎯 Tujuan Pembaruan

Mendukung parsing Condition pada `<Animation>` dan `<Behavior>` untuk membuat sprite yang **pintar** - bisa merasakan posisinya dan memberikan animasi yang sesuai dengan lingkungannya.

## 🚀 Fitur Baru

### 1. Struktur Data Baru

```python
@dataclass
class AnimationBlock:
    """Smart animation block dengan condition support"""
    condition: Optional[str] = None  # "#{mascot.y > 100}"
    frames: List[FrameData] = field(default_factory=list)
    priority: int = 0  # Untuk multiple conditions

@dataclass
class ActionData:
    """Smart action dengan multiple animation blocks"""
    name: str
    action_type: str
    animation_blocks: List[AnimationBlock] = field(default_factory=list)
    border_type: Optional[str] = None
    default_animation: Optional[AnimationBlock] = None  # Fallback animation

@dataclass
class BehaviorData:
    """Smart behavior dengan environment awareness"""
    name: str
    frequency: int
    condition: Optional[str] = None  # "#{mascot.environment.floor.isOn(mascot.anchor)}"
    hidden: bool = False
    next_behaviors: List[str] = field(default_factory=list)
```

### 2. Parsing Condition

**Actions.xml - Multiple Animations:**
```xml
<Action Name="ClimbWall" Type="Move" BorderType="Wall">
    <Animation Condition="#{TargetY < mascot.anchor.y}">
        <!-- Climbing up animation -->
    </Animation>
    <Animation Condition="#{TargetY >= mascot.anchor.y}">
        <!-- Climbing down animation -->
    </Animation>
</Action>
```

**Behaviors.xml - Condition Wrappers:**
```xml
<Condition Condition="#{mascot.environment.floor.isOn(mascot.anchor)}">
    <Behavior Name="WalkAlongFloor" Frequency="100" />
    <Behavior Name="SitDown" Frequency="50" />
</Condition>
```

### 3. JSON Debug Export

```python
# Enable JSON debug mode
parser = XMLParser(save2json=True)

# Results saved to: sprites_json_debug/<sprite_name>.json
```

## 📊 Hasil Parsing

### Sebelum Update:
```
❌ Status: BROKEN
❌ Error: Error parsing actions.xml: invalid predicate
```

### Setelah Update:
```
✅ Status: READY
📋 Actions: 15 loaded (23 animation blocks)
🎯 Behaviors: 45 loaded (12 with conditions)
💾 Saved debug JSON: sprites_json_debug/Hornet.json
```

## 🔧 Cara Penggunaan

### 1. Basic Usage

```python
from src.utils.xml_parser import XMLParser

# Initialize parser
parser = XMLParser(save2json=True)  # Enable JSON debug

# Load all sprite packs
sprite_packs = parser.load_all_sprite_packs()

# Get sprite status
status = parser.get_sprite_status("Hornet")  # READY/PARTIAL/BROKEN
```

### 2. Smart Animation Selection

```python
# Get appropriate animation based on sprite state
sprite_state = {
    'y': 150,
    'on_floor': True,
    'on_wall': False,
    'cursor_nearby': False
}

# Get animation frames for current state
frames = parser.get_animation_for_condition("Hornet", "ClimbWall", sprite_state)

if frames:
    print(f"Found {len(frames)} frames for current state")
```

### 3. Access Parsed Data

```python
# Get all actions for a sprite
actions = parser.get_actions("Hornet")

for action_name, action in actions.items():
    print(f"Action: {action_name}")
    print(f"  Type: {action.action_type}")
    print(f"  Animation blocks: {len(action.animation_blocks)}")
    
    # Check conditional animations
    for block in action.animation_blocks:
        if block.condition:
            print(f"    Condition: {block.condition}")
            print(f"    Frames: {len(block.frames)}")
```

### 4. Behavior Analysis

```python
# Get behaviors with conditions
behaviors = parser.get_behaviors("Hornet")

for behavior_name, behavior in behaviors.items():
    if behavior.condition:
        print(f"Smart behavior: {behavior_name}")
        print(f"  Condition: {behavior.condition}")
        print(f"  Frequency: {behavior.frequency}")
```

## 🎮 Smart Sprite Features

### 1. Environment Awareness

Sprite sekarang bisa:
- **Merasakan posisi**: Di lantai, dinding, atau langit-langit
- **Bereaksi terhadap cursor**: Animasi berbeda saat cursor dekat
- **Mengetahui lingkungan**: Floor, wall, ceiling detection

### 2. Dynamic Animation Selection

```python
# Runtime animation selection based on conditions
def get_smart_animation(sprite_state, action_name):
    frames = parser.get_animation_for_condition("Hornet", action_name, sprite_state)
    return frames or get_default_animation(action_name)
```

### 3. Condition Evaluation

```python
# Basic condition evaluator (dapat diperluas)
def evaluate_condition(condition: str, sprite_state: dict) -> bool:
    # Example conditions:
    # "#{mascot.y > 100}" -> sprite_state['y'] > 100
    # "#{mascot.environment.floor.isOn(mascot.anchor)}" -> sprite_state['on_floor']
    pass
```

## 📁 File Structure

```
learn_shimeji/
├── src/utils/xml_parser.py     # Updated parser
├── sprites_json_debug/         # Debug JSON files (auto-created)
│   ├── Hornet.json
│   ├── HiveKnight.json
│   └── HiveQueen.json
└── test_parser.py              # Test file
```

## 🔍 Debug Features

### 1. JSON Export

Setiap sprite pack akan disimpan sebagai JSON untuk debugging:

```json
{
  "sprite_name": "Hornet",
  "status": "READY",
  "actions": {
    "ClimbWall": {
      "name": "ClimbWall",
      "action_type": "Move",
      "animation_blocks": [
        {
          "condition": "#{TargetY < mascot.anchor.y}",
          "frames": [...]
        },
        {
          "condition": "#{TargetY >= mascot.anchor.y}",
          "frames": [...]
        }
      ]
    }
  }
}
```

### 2. Detailed Logging

```
📁 Validating sprite pack: Hornet
  ✅ Status: READY
  📋 Actions: 15 loaded (23 animation blocks)
  🎯 Behaviors: 45 loaded (12 with conditions)
  💾 Saved debug JSON: sprites_json_debug/Hornet.json
```

## 🚀 Next Steps

### 1. Runtime Integration

```python
# Integrate dengan game engine
class SmartSprite:
    def __init__(self, sprite_name, parser):
        self.sprite_name = sprite_name
        self.parser = parser
        self.state = {'y': 0, 'on_floor': True}
    
    def get_animation(self, action_name):
        return self.parser.get_animation_for_condition(
            self.sprite_name, action_name, self.state
        )
    
    def update_state(self, new_state):
        self.state.update(new_state)
```

### 2. Advanced Condition Evaluator

```python
# Implementasi evaluator yang lebih robust
class ConditionEvaluator:
    def evaluate(self, condition: str, sprite_state: dict) -> bool:
        # Support untuk:
        # - Math operations
        # - Logical operators (&&, ||)
        # - Function calls (isOn, random, etc.)
        # - Environment variables
        pass
```

### 3. Performance Optimization

```python
# Caching untuk evaluasi condition
class CachedConditionEvaluator:
    def __init__(self):
        self.cache = {}
    
    def evaluate(self, condition: str, sprite_state: dict) -> bool:
        cache_key = f"{condition}_{hash(str(sprite_state))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self._evaluate_condition(condition, sprite_state)
        self.cache[cache_key] = result
        return result
```

## ✅ Status Update

- ✅ **Parsing Condition**: Mendukung multiple `<Animation>` dengan condition
- ✅ **Smart Behavior**: Parsing `<Condition>` wrapper di behaviors.xml
- ✅ **JSON Debug**: Export hasil parsing untuk debugging
- ✅ **Backward Compatibility**: Tetap mendukung sprite packs lama
- ✅ **Future-Proof**: Struktur modular untuk fitur baru

## 🎯 Hasil Akhir

Sekarang sprite packs akan:
1. **Berhasil di-parse** tanpa error "invalid predicate"
2. **Mendukung condition** untuk animasi yang dinamis
3. **Menyimpan debug info** ke JSON untuk analisis
4. **Siap untuk smart behavior** di runtime

**Status: READY untuk smart sprite implementation! 🎉** 