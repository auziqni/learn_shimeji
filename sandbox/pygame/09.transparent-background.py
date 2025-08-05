import os
import pygame
import random
import win32gui
import win32con
import win32api

class Sprite:
    def __init__(self, image_path, position=(100, 100)):
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def move(self, dx, dy):
        new_rect = self.rect.copy()
        new_rect.move_ip(dx, dy)
        # Add boundary checking here
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        if 0 <= new_rect.x <= screen_width-new_rect.width:
            self.rect.x = new_rect.x
        if 0 <= new_rect.y <= screen_height-new_rect.height:
            self.rect.y = new_rect.y

def create_transparent_pygame_window():
    """
    FIXED: Buat pygame window dengan Win32 transparency yang benar
    """
    # Set SDL driver sebelum pygame.init()
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    
    # Dapatkan ukuran screen
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    
    # Buat pygame window (borderless)
    display = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Desktop Pet")
    
    # Dapatkan handle window pygame
    hwnd = pygame.display.get_wm_info()["window"]
    
    # Setup Win32 transparency
    # Step 1: Set layered window
    current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    new_style = current_style | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_style)
    
    # Step 2: Set color key transparency (hitam = transparan)
    win32gui.SetLayeredWindowAttributes(
        hwnd,                       # Window handle
        0x000000,                   # Color key: hitam (RGB = 0,0,0)
        0,                          # Alpha (tidak dipakai untuk color key)
        win32con.LWA_COLORKEY      # Mode: color key transparency
    )
    
    # Step 3: Always on top
    win32gui.SetWindowPos(
        hwnd, win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
    )
    
    print(f"✅ Transparent window created: {screen_width}x{screen_height}")
    print(f"✅ Window handle: {hwnd}")
    print("✅ Black pixels will be transparent!")
    
    return display, hwnd, screen_width, screen_height

def main():
    print("🚀 Starting Desktop Pet with Win32 Transparency...")
    
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()
    
    # Create transparent window (FIXED VERSION)
    display, hwnd, screen_width, screen_height = create_transparent_pygame_window()
    
    # Load sprite
    CURRENT_DIR = os.path.dirname(__file__)
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
    image_path = os.path.join(BASE_DIR, "sandbox", "mockSprite", "shime1.png")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("💡 Create a simple test image or update the path")
        # Create simple fallback sprite
        fallback_surface = pygame.Surface((64, 64))
        fallback_surface.fill((255, 0, 0))  # Red square
        pygame.image.save(fallback_surface, "test_sprite.png")
        image_path = "test_sprite.png"
        print(f"✅ Created fallback sprite: {image_path}")
    
    # Create sprites
    sprites = []
    id_sprite = 0
    selected_sprite = None
    dx, dy = 0, 0
    
    # Create 3 sprites (reduced for testing)
    for i in range(3):
        position = (random.randint(100, screen_width-150), 
                   random.randint(100, screen_height-150))
        try:
            sprite = Sprite(image_path, position)
            sprites.append(sprite)
        except pygame.error as e:
            print(f"❌ Error loading sprite: {e}")
            break
    
    if sprites:
        selected_sprite = sprites[id_sprite]
        print(f"✅ Created {len(sprites)} sprites")
    else:
        print("❌ No sprites created!")
        return

    print("\n🎮 Controls:")
    print("  WASD: Move selected sprite")
    print("  Q/E: Switch sprite selection")
    print("  SPACE: Add new sprite")
    print("  ESC: Exit")
    
    # Main game loop
    run = True
    while run:
        # IMPORTANT: Fill with BLACK (will be transparent)
        display.fill((0, 0, 0))  # Black background = transparent!
        
        # Handle movement
        dx, dy = 0, 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx, dy = -2, 0  # Increased speed for visibility
        elif key[pygame.K_d]:
            dx, dy = 2, 0
        elif key[pygame.K_w]:
            dx, dy = 0, -2
        elif key[pygame.K_s]:
            dx, dy = 0, 2
        
        # Draw and move sprites
        for sprite in sprites:
            sprite.draw(display)
            if sprite == selected_sprite:
                # Draw selection indicator (yellow border)
                pygame.draw.rect(display, (255, 255, 0), sprite.rect, 3)
                if dx != 0 or dy != 0:
                    sprite.move(dx, dy)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_q and sprites:
                    id_sprite = (id_sprite - 1) % len(sprites)
                    selected_sprite = sprites[id_sprite]
                    print(f"Selected sprite #{id_sprite}")
                elif event.key == pygame.K_e and sprites:
                    id_sprite = (id_sprite + 1) % len(sprites)
                    selected_sprite = sprites[id_sprite]
                    print(f"Selected sprite #{id_sprite}")
                elif event.key == pygame.K_SPACE:
                    # Add new sprite at random position
                    position = (random.randint(100, screen_width-150), 
                               random.randint(100, screen_height-150))
                    try:
                        new_sprite = Sprite(image_path, position)
                        sprites.append(new_sprite)
                        selected_sprite = new_sprite
                        id_sprite = len(sprites) - 1
                        print(f"Added sprite #{len(sprites)}")
                    except pygame.error as e:
                        print(f"Error adding sprite: {e}")

        clock.tick(60)  # 60 FPS
        pygame.display.flip()

    print("\n🏁 Desktop Pet closed")
    pygame.quit()

if __name__ == "__main__":
    main()