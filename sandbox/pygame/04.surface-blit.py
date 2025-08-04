import pygame

pygame.init()
pygame.display.set_caption("Display Rect Tick Example")
clock = pygame.time.Clock()
display = pygame.display.set_mode((800, 600)) # this is surface
surface = pygame.Surface((500, 500))  # Create a new surface


player_rect = pygame.Rect(100, 100, 50, 50)  # Example rectangle

run = True
while run:
    
    clock.tick(60)  # Limit the frame rate to 60 FPS
    display.fill((0, 0, 0))  # Clear the display with white background
    surface.fill((255, 255, 255))  # Fill the surface with white
    
    # rectea
    pygame.draw.rect(surface, (0, 128, 255), player_rect)  # Draw the rectangle 
    display.blit(surface, (50, 50))  # Blit the surface onto the display at position (50, 50)
    
    
    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        player_rect.move_ip(-1, 0)
    elif key[pygame.K_d]:
        player_rect.move_ip(1, 0)
    elif key[pygame.K_w]:
        player_rect.move_ip(0, -1)
    elif key[pygame.K_s]:
        player_rect.move_ip(0, 1)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

    pygame.display.flip()  # Refresh the display
    
pygame.quit()