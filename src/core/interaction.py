import pygame
import config

class Interaction:
    """Handles movement input and position calculation"""
    
    def __init__(self, speed=config.DEFAULT_MOVEMENT_SPEED):
        self.speed = speed
    
    def get_movement_from_input(self, keys):
        """Calculate movement vector from keyboard input"""
        dx, dy = 0, 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        
        return (dx, dy)
    
    def apply_movement(self, pet, dx, dy):
        """Apply movement to pet"""
        current_x, current_y = pet.get_position()
        new_x = current_x + dx
        new_y = current_y + dy
        pet.set_position(new_x, new_y) 