import os
import pygame
import random


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
        if 0 <= new_rect.x <= 800-new_rect.width:
            self.rect.x = new_rect.x
        if 0 <= new_rect.y <= 800-new_rect.height:
            self.rect.y = new_rect.y
            


def main():
    pygame.init()
    pygame.display.set_caption("Display Rect Tick Example")
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((800, 800))  # this is surface
    
    
    CURRENT_DIR = os.path.dirname(__file__)  # -> /pygame/
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))  # -> / (project-root)
    image_path = os.path.join(BASE_DIR, "sandbox", "mockSprite", "shime1.png")  # Path to the image
    
    sprites = []
    id_sprite = 0
    selected_sprite = None
    dx, dy = 0, 0
    
    
    for i in range(5):  # Create 5 random sprites
        position = (random.randint(0, 750), random.randint(0, 750))
        sprite = Sprite(image_path, position)   
        sprites.append(sprite)
        
    if sprites:
        selected_sprite = sprites[id_sprite]
    
    
    

    run = True
    while run:
        display.fill((0, 0, 0))  # Clear the display with black background
        
        dx, dy = 0, 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a]:
            dx, dy = -1, 0
        elif key[pygame.K_d]:
            dx, dy = 1, 0
        elif key[pygame.K_w]:
            dx, dy = 0, -1
        elif key[pygame.K_s]:
            dx, dy = 0, 1
        
        for sprite in sprites:
            sprite.draw(display)
            if sprite == selected_sprite:
                # draw a rectangle around the selected sprite
                pygame.draw.rect(display, (255, 255, 0), sprite.rect, 2)
                if dx != 0 or dy != 0:
                    sprite.move(dx, dy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_q and sprites:
                    id_sprite = (id_sprite - 1) % len(sprites)
                    selected_sprite = sprites[id_sprite]
                elif event.key == pygame.K_e and sprites:
                    id_sprite = (id_sprite + 1) % len(sprites)
                    selected_sprite = sprites[id_sprite]

        clock.tick(60)  # Limit the frame rate to 60 FPS
        pygame.display.flip()  # Refresh the display

    pygame.quit()
    
    
if __name__ == "__main__":
    main()