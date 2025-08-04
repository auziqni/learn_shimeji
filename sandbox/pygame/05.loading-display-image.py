import pygame
import os

pygame.init()
pygame.display.set_caption("Display Rect Tick Example")
clock = pygame.time.Clock()
display = pygame.display.set_mode((800, 800)) # this is surface
surface = pygame.Surface((200, 200))  # Create a new surface

CURRENT_DIR = os.path.dirname(__file__)                  # -> /pygame/
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..",".."))  # -> / (project-root)

image_path = os.path.join(BASE_DIR,"sandbox","mockSprite", "shime1.png")  # Path to the image
sprite = pygame.image.load(image_path)  # Load the image

# sprite_rect = sprite.get_rect()  # Get the rectangle of the sprite
# sprite_rect.x = 100  # Set initial x position
# sprite_rect.y = 100  # Set initial y position

sprite_rect = sprite.get_rect(topleft=(100, 100))

run = True
while run:
    
    clock.tick(60)  # Limit the frame rate to 60 FPS
    display.fill((0, 0, 0))  # Clear the display with white background
    surface.fill((255, 255, 255))  # Fill the surface with white
    
    # rectea
    
    # pygame.draw.rect(surface, (0, 128, 255), sprite_image.get_rect())  # Draw the rectangle
    surface.blit(sprite, sprite_rect)  # Blit the sprite image onto the surface
    display.blit(surface, (300, 300))  # Blit the surface onto the display at position (50, 50)
    
    
    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        sprite_rect.move_ip(-1, 0)
    elif key[pygame.K_d]:
        sprite_rect.move_ip(1, 0)
    elif key[pygame.K_w]:
        sprite_rect.move_ip(0, -1)
    elif key[pygame.K_s]:
        sprite_rect.move_ip(0, 1)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

    pygame.display.flip()  # Refresh the display
    
pygame.quit()