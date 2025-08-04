import pygame

pygame.init()

display = pygame.display.set_mode((800, 600))

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            run = False

pygame.quit()