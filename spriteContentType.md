# Sprite Content Type Documentation

## 📋 Quick Reference

| Section | Purpose | Key Fields |
|---------|---------|------------|
| **Sprite Info** | File identification | `sprite_name` |
| **Actions** | Animation & behavior logic | `action_type`, `animations`, `embedded_data` |
| **Behaviors** | AI decision making | `frequency`, `condition`, `next_behaviors` |

---

## 🏗️ JSON Structure Overview

### 1. **Sprite Information**
```json
{
  "sprite_name": "Hornet"
}
```

**Purpose**: Sprite pack identification

---

### 2. **Actions Section**
```json
{
  "actions": {
    "ActionName": {
      "name": "ActionName",
      "action_type": "Stay|Move|Animate|Sequence|Embedded",
      "border_type": "Floor|Wall|Ceiling|null",
      "draggable": true|false|null,
      "loop": true|false|null,
      "animations": {},
      "action_references": [],
      "embedded_data": {}
    }
  }
}
```

#### **Action Types:**

| Type | Purpose | Characteristics |
|------|---------|----------------|
| **Stay** | Static animations | No movement, looping |
| **Move** | Movement animations | Has velocity, border interaction |
| **Animate** | Simple animations | Visual effects, sound |
| **Sequence** | Complex behaviors | Multiple actions, conditions |
| **Embedded** | System integration | Java classes, IE interaction |

#### **Key Fields:**
- **`action_type`**: Determines behavior category
- **`animations`**: Frame data for visual effects
- **`embedded_data`**: Java class references (for Embedded type)
- **`action_references`**: Action chaining (for Sequence type)

---

### 3. **Behaviors Section**
```json
{
  "behaviors": {
    "BehaviorName": {
      "name": "BehaviorName",
      "frequency": 0-100,
      "hidden": true|false,
      "condition": "expression|null",
      "next_behaviors": ["Behavior1", "Behavior2"],
      "action": "ActionName|null",
      "type": "system|ai|interaction|transition"
    }
  }
}
```

#### **Behavior Types:**

| Type | Frequency | Purpose |
|------|-----------|---------|
| **system** | 0 | Essential behaviors (ChaseMouse, Fall) |
| **ai** | 1-100 | AI-driven behaviors (environment-based) |
| **interaction** | 0 | User-triggered behaviors (Pet, BePet) |
| **transition** | 0 | Temporary behaviors (bridging states) |

#### **Key Fields:**
- **`frequency`**: Selection probability (0 = always, 1-100 = random)
- **`condition`**: Environment-based activation rules
- **`next_behaviors`**: Possible follow-up behaviors
- **`hidden`**: UI visibility (true = hidden from user)

---

## 🎯 **Field Descriptions**

### **Action Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Action identifier | "Walk", "Sit" |
| `action_type` | string | Behavior category | "Stay", "Move", "Embedded" |
| `border_type` | string|null | Boundary interaction | "Floor", "Wall", null |
| `draggable` | boolean|null | User drag capability | true, false, null |
| `loop` | boolean|null | Animation looping | true, false, null |
| `animations` | object | Frame data collection | `{"default": {...}}` |
| `action_references` | array | Sequence actions | `[{"name": "Action1"}]` |
| `embedded_data` | object | Java class data | `{"class": "com.example.Action"}` |

### **Behavior Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Behavior identifier | "ChaseMouse", "Pet" |
| `frequency` | number | Selection probability | 0, 50, 100 |
| `hidden` | boolean | UI visibility | true, false |
| `condition` | string|null | Activation expression | `"#{mascot.y > 100}"` |
| `next_behaviors` | array | Follow-up behaviors | `["SitDown", "Walk"]` |
| `action` | string|null | Associated action | "Walk", null |
| `type` | string | Behavior category | "system", "ai", "interaction" |

### **Animation Fields:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `image` | string | Sprite file path | "shime1.png" |
| `duration` | number | Frame duration (seconds) | 1.0, 0.133 |
| `velocity` | array | Movement speed [x, y] | [0, 0], [-2, 0] |
| `imageAnchor` | array | Anchor point [x, y] | [64, 128] |
| `sound` | string|null | Audio file path | "bounce.wav", null |
| `volume` | number|null | Sound volume (-100 to 0) | -14, null |

---

## 🔄 **Data Flow**

```
XML Files → JSON Converter → data.json → JSONParser → Runtime
     ↓              ↓              ↓           ↓
actions.xml   →   Actions    →   Actions   →   Animation
behaviors.xml →   Behaviors  →   Behaviors →   Behavior Logic
```

---

## ⚠️ **Important Notes**

### **Required Fields:**
- `sprite_name`: Always present
- `actions`: Always present (can be empty)
- `behaviors`: Always present (can be empty)

### **Optional Fields:**
- `border_type`: Can be null
- `draggable`: Can be null
- `loop`: Can be null
- `condition`: Can be null
- `action`: Can be null

### **Data Types:**
- **Numbers**: Use integers for frequency, floats for duration
- **Booleans**: Use true/false, not "true"/"false"
- **Arrays**: Use square brackets `[]`
- **Objects**: Use curly braces `{}`

---

## 🎮 **Usage Examples**

### **Simple Stay Action:**
```json
{
  "name": "Stand",
  "action_type": "Stay",
  "border_type": "Floor",
  "animations": {
    "default": {
      "frames": [
        {
          "image": "/shime1.png",
          "duration": 75.0,
          "velocity": [0.0, 0.0],
          "imageAnchor": [64.0, 128.0]
        }
      ]
    }
  }
}
```

### **Complex AI Behavior:**
```json
{
  "name": "WalkAlongIECeiling",
  "frequency": 100,
  "hidden": true,
  "condition": "#{mascot.environment.activeIE.topBorder.isOn(mascot.anchor)}",
  "next_behaviors": [],
  "action": null,
  "type": "ai"
}
```

### **Embedded Action:**
```json
{
  "name": "FallWithIe",
  "action_type": "Embedded",
  "animations": {}
}
```

### **Animation with Sound:**
```json
{
  "image": "/shime48.png",
  "duration": 3.0,
  "velocity": [0.0, 0.0],
  "imageAnchor": [64.0, 198.0],
  "sound": "/Hive Knight 5.wav",
  "volume": -7
}
```

---

## 📊 **File Statistics (Current Implementation)**

| Component | Hornet | HiveKnight | HiveQueen |
|-----------|--------|------------|-----------|
| **Actions** | 105 | 103 | 107 |
| **Behaviors** | 69 | 67 | 71 |
| **Embedded Actions** | 12 | 12 | 12 |
| **Sequence Actions** | 58 | 56 | 60 |
| **AI Behaviors** | 54 | 52 | 56 |
| **System Behaviors** | 5 | 5 | 5 |

---

## 🔧 **Quick Troubleshooting**

| Issue | Check | Solution |
|-------|-------|----------|
| **Invalid JSON** | JSON syntax | Validate with JSON parser |
| **Missing Actions** | `actions` field | Ensure actions exist |
| **Missing Behaviors** | `behaviors` field | Ensure behaviors exist |
| **Invalid References** | `next_behaviors` | Verify behavior names exist |
| **Missing Images** | `image` paths | Check file existence |
| **Invalid Conditions** | `condition` syntax | Validate expression format |

---

## 📝 **Best Practices**

1. **Naming**: Use descriptive names for actions and behaviors
2. **Frequency**: Use 0 for system behaviors, 1-100 for AI behaviors
3. **Conditions**: Keep expressions simple and readable
4. **References**: Always verify referenced behaviors exist
5. **Image Anchors**: Use consistent anchor points (typically [64, 128])
6. **Documentation**: Add comments for complex conditions

---

## 🚀 **Implementation Notes**

### **Current Status:**
- ✅ **JSON Structure**: Matches actual implementation
- ✅ **Field Types**: All field types are accurate
- ✅ **Examples**: Based on real data from assets
- ✅ **Statistics**: Updated with current file counts

### **Deprecated Sections (Removed):**
- ❌ **Metadata Section**: Not present in actual JSON
- ❌ **Validation Section**: Not present in actual JSON
- ❌ **Conversion Tracking**: Not implemented

### **Updated Sections:**
- ✅ **Sprite Info**: Simplified to match actual structure
- ✅ **Actions**: Accurate field descriptions
- ✅ **Behaviors**: Accurate field descriptions
- ✅ **Examples**: Real examples from Hornet sprite pack

---

*This documentation covers the essential structure of sprite JSON files for Shimeji desktop pets, updated to match the actual implementation.* 