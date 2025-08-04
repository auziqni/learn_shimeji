"""
Pygame Basic Tutorial - Window dan Sprite Spawning
==================================================

File ini berisi tutorial sederhana untuk:
1. Membuat window Pygame
2. Menampilkan sprite
3. Spawn multiple sprites
4. Game loop dasar

Author: Shimeji Project
"""

import pygame
import os
import random

# ============================================================================
# 1. INISIALISASI PYGAME
# ============================================================================

# Inisialisasi semua modul Pygame
# Ini harus dipanggil sebelum menggunakan fitur Pygame apapun
pygame.init()

# ============================================================================
# 2. KONFIGURASI WINDOW
# ============================================================================

# Ukuran window (width, height)
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Membuat window dengan ukuran yang ditentukan
# set_mode() mengembalikan Surface object yang merepresentasikan window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Set judul window (akan muncul di title bar)
pygame.display.set_caption("Shimeji Desktop Pet - Basic Tutorial")

# ============================================================================
# 3. KONFIGURASI GAME
# ============================================================================

# Clock untuk mengontrol FPS (Frame Per Second)
# Ini penting untuk menjaga game berjalan dengan kecepatan yang konsisten
clock = pygame.time.Clock()
FPS = 60  # Target 60 FPS

# Flag untuk mengontrol game loop
running = True

# ============================================================================
# 4. SPRITE MANAGEMENT
# ============================================================================

class SimpleSprite:
    """
    Class sederhana untuk mengelola sprite
    Setiap sprite memiliki posisi dan gambar
    """
    
    def __init__(self, image_path, x, y):
        """
        Inisialisasi sprite
        
        Args:
            image_path (str): Path ke file gambar sprite
            x (int): Posisi X sprite
            y (int): Posisi Y sprite
        """
        # Load gambar sprite dari file
        # pygame.image.load() mengembalikan Surface object
        self.image = pygame.image.load(image_path)
        
        # Dapatkan ukuran gambar
        self.rect = self.image.get_rect()
        
        # Set posisi sprite
        self.rect.x = x
        self.rect.y = y
        
        # Kecepatan sprite (untuk animasi sederhana)
        self.speed_x = random.randint(-2, 2)  # Kecepatan random
        self.speed_y = random.randint(-2, 2)
        
    def update(self):
        """
        Update posisi sprite berdasarkan kecepatan
        """
        # Update posisi berdasarkan kecepatan
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off boundaries (memantul dari tepi window)
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.speed_x *= -1  # Balik arah horizontal
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.speed_y *= -1  # Balik arah vertikal
            
    def draw(self, surface):
        """
        Gambar sprite ke surface
        
        Args:
            surface: Surface object tempat sprite akan digambar
        """
        # blit() adalah method untuk menggambar satu surface ke surface lain
        # surface.blit(source_surface, position)
        surface.blit(self.image, self.rect)

# ============================================================================
# 5. MEMBUAT SPRITES
# ============================================================================

# List untuk menyimpan semua sprites
sprites = []

# Path ke sprite (gunakan sprite yang sudah ada di mockSprite)
sprite_path = os.path.join("mockSprite", "shime1.png")

# Spawn beberapa sprites dengan posisi random
print("Spawning sprites...")
for i in range(5):  # Buat 5 sprites
    # Posisi random
    x = random.randint(0, WINDOW_WIDTH - 50)  # -50 untuk memastikan sprite tidak keluar window
    y = random.randint(0, WINDOW_HEIGHT - 50)
    
    # Buat sprite baru
    sprite = SimpleSprite(sprite_path, x, y)
    sprites.append(sprite)
    print(f"Sprite {i+1} spawned at ({x}, {y})")

# ============================================================================
# 6. GAME LOOP
# ============================================================================

print("Starting game loop...")
print("Press ESC to quit")
print("Press SPACE to spawn new sprite")

while running:
    # ========================================================================
    # 6.1 EVENT HANDLING
    # ========================================================================
    
    # pygame.event.get() mengembalikan list semua event yang terjadi
    # Event bisa berupa mouse click, keyboard press, window close, dll
    for event in pygame.event.get():
        
        # Event ketika user menutup window
        if event.type == pygame.QUIT:
            running = False
            
        # Event ketika keyboard ditekan
        elif event.type == pygame.KEYDOWN:
            # ESC key untuk keluar
            if event.key == pygame.K_ESCAPE:
                running = False
                
            # SPACE key untuk spawn sprite baru
            elif event.key == pygame.K_SPACE:
                x = random.randint(0, WINDOW_WIDTH - 50)
                y = random.randint(0, WINDOW_HEIGHT - 50)
                new_sprite = SimpleSprite(sprite_path, x, y)
                sprites.append(new_sprite)
                print(f"New sprite spawned at ({x}, {y})")
                print(f"Total sprites: {len(sprites)}")
    
    # ========================================================================
    # 6.2 UPDATE GAME LOGIC
    # ========================================================================
    
    # Update semua sprites
    for sprite in sprites:
        sprite.update()
    
    # ========================================================================
    # 6.3 RENDERING
    # ========================================================================
    
    # Fill screen dengan warna putih
    # RGB: (255, 255, 255) = putih
    screen.fill((255, 255, 255))
    
    # Draw semua sprites
    for sprite in sprites:
        sprite.draw(screen)
    
    # Update display
    # pygame.display.flip() menampilkan semua yang sudah di-draw
    pygame.display.flip()
    
    # ========================================================================
    # 6.4 FPS CONTROL
    # ========================================================================
    
    # clock.tick(FPS) memastikan game berjalan dengan FPS yang ditentukan
    # Ini penting untuk konsistensi kecepatan game
    clock.tick(FPS)

# ============================================================================
# 7. CLEANUP
# ============================================================================

print("Game ended. Cleaning up...")
pygame.quit()

"""
PENJELASAN KONSEP PENTING:
==========================

1. GAME LOOP:
   - Event Handling: Menangani input user
   - Update: Update logika game (posisi, collision, dll)
   - Render: Gambar semua objek ke screen
   - FPS Control: Jaga kecepatan game konsisten

2. SURFACE:
   - Surface adalah "canvas" untuk menggambar
   - screen adalah Surface utama (window)
   - sprite.image juga Surface

3. RECT:
   - Rect adalah rectangle (persegi panjang) untuk posisi dan collision
   - Setiap Surface memiliki rect
   - rect.x, rect.y adalah posisi
   - rect.width, rect.height adalah ukuran

4. BLIT:
   - Method untuk menggambar satu Surface ke Surface lain
   - Format: destination_surface.blit(source_surface, position)

5. EVENT:
   - Event adalah kejadian yang terjadi (mouse click, keyboard, dll)
   - Harus di-handle dalam game loop
   - pygame.QUIT untuk menutup window

CONTROLS:
=========
- ESC: Keluar dari game
- SPACE: Spawn sprite baru
- Mouse: Klik close button untuk keluar

TIPS:
=====
- Selalu panggil pygame.init() di awal
- Selalu panggil pygame.quit() di akhir
- Gunakan clock.tick() untuk kontrol FPS
- Handle events dalam game loop
- Update sebelum render

PERFORMANCE TIPS:
================
- Batasi jumlah sprite untuk performa yang baik
- Gunakan sprite caching untuk sprite yang sering digunakan
- Optimasi collision detection untuk banyak objek
- Monitor FPS untuk memastikan game berjalan lancar
""" 