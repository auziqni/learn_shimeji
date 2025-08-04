import pygame
import os

pygame.init()
pygame.display.set_caption("Display Rect Tick Example")
clock = pygame.time.Clock()
display = pygame.display.set_mode((800, 800)) # this is surface

CURRENT_DIR = os.path.dirname(__file__)                  # -> /pygame/
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..",".."))  # -> / (project-root)

image_path = os.path.join(BASE_DIR,"sandbox","mockSprite", "shime1.png")  # Path to the image
sprite = pygame.image.load(image_path)  # Load the image
sprite2 = pygame.image.load(image_path)  # Load the image


# sprite_rect = sprite.get_rect()  # Get the rectangle of the sprite
# sprite_rect.x = 100  # Set initial x position
# sprite_rect.y = 100  # Set initial y position

sprite_rect = sprite.get_rect(topleft=(100, 100))
sprite2_rect = sprite2.get_rect(topleft=(200, 200))  # Another sprite rectangle

holder_sprite_rect = sprite_rect  # To hold the current sprite rectangle for control

run = True
while run:
    
    clock.tick(60)  # Limit the frame rate to 60 FPS
    display.fill((0, 0, 0))  # Clear the display with white background
    
    # rectea
    
    # pygame.draw.rect(surface, (0, 128, 255), sprite_image.get_rect())  # Draw the rectangle
    display.blit(sprite, sprite_rect)  # Blit the sprite image onto the surface
    display.blit(sprite2, sprite2_rect)  # Blit another sprite image onto the display
    
    # switch to control the first sprite
    if pygame.key.get_pressed()[pygame.K_q]:
        holder_sprite_rect = sprite_rect
    elif pygame.key.get_pressed()[pygame.K_e]:
        holder_sprite_rect = sprite2_rect
        
    
    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        holder_sprite_rect.move_ip(-1, 0)
    elif key[pygame.K_d]:
        holder_sprite_rect.move_ip(1, 0)
    elif key[pygame.K_w]:
        holder_sprite_rect.move_ip(0, -1)
    elif key[pygame.K_s]:
        holder_sprite_rect.move_ip(0, 1)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

    pygame.display.flip()  # Refresh the display
    
pygame.quit()