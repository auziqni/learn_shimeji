# 🐛 Pet Debug Info Feature

## 📋 **Overview**

Fitur **Pet Debug Info** menampilkan informasi detail setiap pet di sebelah kanan pet dalam mode debug. Informasi ini membantu developer dan user untuk memahami status dan data setiap pet secara real-time.

## 🎯 **Informasi yang Ditampilkan**

### **✅ Data Pet yang Ditampilkan (Final Format)**
1. **Sprite Name : Pet Name**: Nama sprite pack dan pet (selalu ditampilkan keduanya)
2. **Action Info**: Informasi action saat ini (format: "actiontype : actionname")
3. **Position**: Koordinat posisi pet (x y) - format tanpa koma

### **🎨 Warna Kode**
- **🟡 Yellow**: Sprite Name : Pet Name
- **⚪ White**: Action Info
- **🔴 Light Red**: Position

## 🔧 **Implementasi Teknis**

### **1. DebugManager Enhancement**
```python
def draw_pet_debug_info(self, surface, pet, pet_index):
    """Draw debug info for a specific pet to the right of the pet"""
    if not self.debug_mode or not self.font or not pet:
        return
    
    # Get pet data
    sprite_name = pet.get_current_sprite_pack()
    pet_name = pet.get_name()
    chat = pet.get_chat()
    position = pet.get_position()
    
    # Line 1: Sprite Name : Pet Name (always show both)
    combined_text = f"{sprite_name} : {pet_name}"
    
    # Line 2: Action info (simplified)
    # Extract action type and name from chat
    
    # Line 3: Position (without comma)
    pos_text = f"({pet_x} {pet_y})"
```

### **2. UI Manager Integration**
```python
def _render_pet_debug_info(self, surface, game_state):
    """Render debug info for each pet"""
    debug_manager = game_state.get('debug_manager')
    pet_manager = game_state.get('pet_manager')
    
    if debug_manager and pet_manager and debug_manager.debug_mode:
        for i, pet in enumerate(pet_manager.pets):
            debug_manager.draw_pet_debug_info(surface, pet, i)
```

## 🎮 **Cara Menggunakan**

### **1. Aktifkan Debug Mode**
```
F1 → Toggle debug mode ON
```

### **2. Lihat Debug Info**
- Debug info akan muncul di sebelah kanan setiap pet
- Informasi ditampilkan dalam format yang mudah dibaca
- Warna berbeda untuk setiap jenis informasi

### **3. Contoh Output (Final Format)**
```
Hornet : Hornet
Stay : idle
(150 200)
```

Atau jika sprite name dan pet name berbeda:
```
Hornet : CustomName
Move : walk_right
(180 200)
```

## 📊 **Data Source**

### **✅ Pet Data Methods**
```python
# Sprite name
sprite_name = pet.get_current_sprite_pack()

# Pet name  
pet_name = pet.get_name()

# Chat/Action info
chat = pet.get_chat()

# Position
position = pet.get_position()
```

### **✅ Data Flow**
1. **Pet Creation** → Data disimpan dalam Pet object
2. **UI Rendering** → DebugManager mengambil data dari Pet
3. **Display** → Informasi dirender di sebelah kanan pet

## 🎯 **Features**

### **✅ Consistent Format**
- **Always Show Both**: Sprite name dan pet name selalu ditampilkan keduanya
- **Uniform Display**: Semua pet memiliki format yang sama
- **Clean Position**: Format posisi tanpa koma untuk tampilan yang lebih bersih

### **✅ Smart Text Handling**
- **Consistent Display**: Format `<SpriteName> : <PetName>` untuk semua pet
- **Text Truncation**: Potong text yang terlalu panjang (>30 chars)
- **Error Handling**: Graceful fallback jika ada error

### **✅ Debug Mode Only**
- Hanya muncul saat debug mode ON
- Tidak mengganggu tampilan normal
- Mudah di-toggle dengan F1

### **✅ Color-coded Information**
- Setiap jenis informasi memiliki warna berbeda
- Mudah dibedakan secara visual
- Konsisten dengan debug system lainnya

## 🔍 **Technical Details**

### **Positioning Logic**
```python
# Calculate position for debug info (to the right of pet)
pet_x, pet_y = position
pet_width = pet.width
debug_x = pet_x + pet_width + 10  # 10px to the right of pet
debug_y = pet_y
```

### **Text Processing**
```python
# Always show both sprite name and pet name
combined_text = f"{sprite_name} : {pet_name}"

# Extract action info from chat
if " : " in chat:
    action_parts = chat.split(" : ", 1)
    if len(action_parts) == 2:
        action_type, action_name = action_parts
        chat_text = f"{action_type} : {action_name}"

# Position without comma
pos_text = f"({pet_x} {pet_y})"
```

### **Error Handling**
```python
try:
    # Render debug info
    # ...
except Exception as e:
    # Silently fail if rendering fails
    pass
```

## 🎉 **Benefits**

### **✅ Developer Experience**
- **Consistent Format**: Semua pet memiliki format yang sama
- **Clear Identification**: Mudah membedakan sprite name dan pet name
- **Clean Position**: Format posisi yang lebih bersih
- **Quick Debugging**: Informasi yang mudah dibaca dan dipahami

### **✅ User Experience**
- **Uniform Display**: Tampilan yang konsisten untuk semua pet
- **Better Readability**: Format yang lebih mudah dibaca
- **Non-intrusive**: Tidak mengganggu gameplay normal
- **Toggle-able**: Mudah diaktifkan/nonaktifkan

### **✅ Code Quality**
- **Modular Design**: Terpisah dari rendering utama
- **Error Handling**: Graceful fallback jika ada error
- **Performance**: Minimal impact pada performance
- **Maintainable**: Mudah di-extend dan di-modify

## 🚀 **Future Enhancements**

### **Planned Features**
- [ ] Action type display
- [ ] Volume level display
- [ ] Sound status display
- [ ] Animation frame info
- [ ] Memory usage per pet

### **Advanced Features**
- [ ] Clickable debug info
- [ ] Expandable/collapsible info
- [ ] Custom debug info layout
- [ ] Debug info export
- [ ] Performance metrics per pet

## 📝 **Usage Examples**

### **Example 1: Same Sprite and Pet Name**
```
Hornet : Hornet
Stay : idle
(150 200)
```

### **Example 2: Different Sprite and Pet Name**
```
Hornet : CustomName
Move : walk_right
(180 200)
```

### **Example 3: Action Change**
```
HiveKnight : HiveKnight
Animate : attack
(220 200)
```

### **Example 4: Long Text Truncation**
```
VeryLongSpriteName : VeryLongPetName...
Stay : very_long_action_na...
(150 200)
```

---

**🎉 Pet Debug Info feature telah diperbaiki! Format yang konsisten dan bersih.** ✅ 