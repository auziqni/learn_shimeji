# Animation System Refactor - Integration with JSON Parser

## 🎯 Overview

Refactor `animation.py` untuk terintegrasi dengan `json_parser.py` dan mendukung sistem desktop pets yang lebih modular dan scalable.

## 🔄 Changes Made

### 1. **Animation Class Updates**

#### **Before (XML-based):**
```python
def __init__(self, sprite_pack_path: str, animation_name: str, frames_data: List[Dict]):
    # frames_data: List of frame dictionaries from XML parser
    image_path = frame_data.get('Image', '')
    image_anchor = self._parse_anchor(frame_data.get('ImageAnchor', '64,128'))
    velocity = self._parse_velocity(frame_data.get('Velocity', '0,0'))
    duration = int(frame_data.get('Duration', 1))
```

#### **After (JSON-based):**
```python
def __init__(self, sprite_pack_path: str, animation_name: str, frames_data: List[FrameData]):
    # frames_data: List of FrameData from JSON parser
    image_path = frame_data.image
    velocity = frame_data.velocity
    duration = int(frame_data.duration * 30)  # Convert seconds to frames (30 FPS)
    sound = frame_data.sound
    volume = frame_data.volume
```

### 2. **New AnimationManager Class**

Menambahkan `AnimationManager` sebagai central controller yang terintegrasi dengan JSON parser:

```python
class AnimationManager:
    """
    Central animation manager that integrates with JSON parser
    Manages multiple animations and pets simultaneously
    """
    
    def __init__(self, json_parser: JSONParser):
        self.json_parser = json_parser
        self.animations: Dict[str, Dict[str, Animation]] = {}
        self.active_animations: Dict[str, Animation] = {}
```

#### **Key Features:**
- **JSON Parser Integration**: Menggunakan `JSONParser` untuk load sprite data
- **Multi-Pet Support**: Mengelola multiple pets dengan unique IDs
- **Action Management**: Load dan manage semua actions dari sprite pack
- **Performance Optimization**: Shared sprite cache untuk memory efficiency

### 3. **Enhanced Data Flow**

#### **New Data Flow:**
```
JSON Parser → AnimationManager → Individual Animations → Pet Instances
```

#### **Integration Points:**
1. **JSON Parser**: Load sprite pack data (`ActionData`, `FrameData`)
2. **AnimationManager**: Central controller untuk semua animations
3. **Animation**: Individual animation instances untuk setiap pet
4. **Pet Management**: Unique pet IDs dengan individual animation states

## 🚀 New Features

### 1. **Smart Animation Loading**
```python
# Load all animations for a sprite
animation_manager.load_sprite_animations("Hornet")

# Get available actions
actions = animation_manager.get_available_actions("Hornet")
```

### 2. **Multi-Pet Animation Management**
```python
# Start animation for specific pet
animation_manager.start_animation("pet_001", "Hornet", "Walk")

# Update pet animation
animation_manager.update_pet_animation("pet_001", delta_time)

# Stop pet animation
animation_manager.stop_pet_animation("pet_001")
```

### 3. **Performance Optimizations**
- **Global Sprite Cache**: Shared cache untuk semua animations
- **Memory Efficiency**: Optimized untuk 25+ concurrent pets
- **Sound Caching**: Efficient sound loading dan management

## 📊 Benefits

### 1. **Modularity**
- ✅ Separation of concerns antara data parsing dan animation
- ✅ Reusable animation components
- ✅ Clean interfaces antara components

### 2. **Scalability**
- ✅ Support untuk 25+ pets simultaneously
- ✅ Efficient memory management
- ✅ Centralized animation control

### 3. **Maintainability**
- ✅ JSON-first approach (modern data format)
- ✅ Clear data structures (`ActionData`, `FrameData`)
- ✅ Comprehensive error handling

### 4. **Performance**
- ✅ Shared sprite cache untuk memory efficiency
- ✅ Optimized animation updates
- ✅ Efficient pet management

## 🔧 Usage Examples

### **Basic Integration:**
```python
# Initialize systems
json_parser = JSONParser(assets_dir="assets")
animation_manager = AnimationManager(json_parser)

# Load sprite animations
animation_manager.load_sprite_animations("Hornet")

# Start pet animation
animation_manager.start_animation("pet_001", "Hornet", "Walk")

# Update in game loop
animation_manager.update_pet_animation("pet_001", delta_time)
```

### **Advanced Usage:**
```python
# Get all available actions
actions = animation_manager.get_available_actions("Hornet")

# Create multiple pets
for i in range(5):
    pet_id = f"pet_{i:03d}"
    animation_manager.start_animation(pet_id, "Hornet", "Stay")

# Update all pets
for pet_id in active_pets:
    animation_manager.update_pet_animation(pet_id, delta_time)
```

## 🧪 Testing

### **Integration Test:**
```bash
python test/test_animation_integration.py
```

### **Test Coverage:**
- ✅ Animation loading dari JSON parser
- ✅ Multi-pet animation management
- ✅ Performance testing dengan multiple pets
- ✅ Cache management testing
- ✅ Error handling testing

## 📈 Performance Metrics

### **Memory Usage:**
- **Before**: Individual sprite loading per animation
- **After**: Shared sprite cache untuk semua animations

### **Scalability:**
- **Target**: 25+ concurrent pets
- **Memory**: Optimized sprite caching
- **Performance**: 30 FPS target dengan multiple pets

## 🔮 Future Enhancements

### 1. **Advanced Animation Features**
- [ ] Conditional animations berdasarkan environment
- [ ] Complex animation sequences
- [ ] Sound synchronization improvements

### 2. **Performance Optimizations**
- [ ] Lazy loading untuk large sprite packs
- [ ] Background sprite preloading
- [ ] Memory usage monitoring

### 3. **Integration Features**
- [ ] Real-time rendering system
- [ ] User interaction handling
- [ ] Environment boundary detection

## 📝 Migration Guide

### **From Old System:**
```python
# Old way (XML-based)
animation = Animation(sprite_path, "Walk", xml_frames_data)
```

### **To New System:**
```python
# New way (JSON-based)
json_parser = JSONParser(assets_dir="assets")
animation_manager = AnimationManager(json_parser)
animation_manager.load_sprite_animations("Hornet")
animation = animation_manager.get_animation("Hornet", "Walk")
```

## ✅ Summary

Refactor ini berhasil mengintegrasikan `animation.py` dengan `json_parser.py` untuk menciptakan sistem yang:

1. **Modular**: Clean separation antara data parsing dan animation
2. **Scalable**: Support untuk multiple pets dengan efficient memory usage
3. **Maintainable**: Modern JSON-based data structures
4. **Performant**: Optimized caching dan update system

Sistem ini siap untuk pengembangan lebih lanjut menuju MVP goals yang didefinisikan di `sprint.md`. 