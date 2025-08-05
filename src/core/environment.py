import pygame
import random
import config

class Environment:
    """Handles all boundary-related logic and virtual environment detection"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.boundaries = self._calculate_boundaries()
    
    def _calculate_boundaries(self):
        """Calculate boundary positions"""
        return {
            'left_wall': int(self.screen_width * config.DEFAULT_BOUNDARY_MARGIN),
            'right_wall': int(self.screen_width * (1 - config.DEFAULT_BOUNDARY_MARGIN)),
            'ceiling': int(self.screen_height * config.DEFAULT_BOUNDARY_MARGIN),
            'floor': int(self.screen_height * (1 - config.DEFAULT_BOUNDARY_MARGIN))
        }
    
    def check_collision(self, pet):
        """Check if pet collides with boundaries"""
        rect = pet.get_rect()
        collisions = {
            'left': rect.left < self.boundaries['left_wall'],
            'right': rect.right > self.boundaries['right_wall'],
            'top': rect.top < self.boundaries['ceiling'],
            'bottom': rect.bottom > self.boundaries['floor']
        }
        return collisions
    
    def clamp_position(self, pet):
        """Clamp pet position to boundaries"""
        x, y = pet.get_position()
        
        # Clamp X
        if x < self.boundaries['left_wall']:
            x = self.boundaries['left_wall']
        elif x + pet.width > self.boundaries['right_wall']:
            x = self.boundaries['right_wall'] - pet.width
        
        # Clamp Y
        if y < self.boundaries['ceiling']:
            y = self.boundaries['ceiling']
        elif y + pet.height > self.boundaries['floor']:
            y = self.boundaries['floor'] - pet.height
        
        pet.set_position(x, y)
    
    def get_safe_spawn_position(self, pet_width, pet_height):
        """Get random position within boundaries"""
        x = random.randint(
            self.boundaries['left_wall'] + config.SAFE_SPAWN_MARGIN,
            max(self.boundaries['left_wall'] + config.SAFE_SPAWN_MARGIN + 1, 
                self.boundaries['right_wall'] - pet_width - config.SAFE_SPAWN_MARGIN)
        )
        y = random.randint(
            self.boundaries['ceiling'] + config.SAFE_SPAWN_MARGIN,
            max(self.boundaries['ceiling'] + config.SAFE_SPAWN_MARGIN + 1, 
                self.boundaries['floor'] - pet_height - config.SAFE_SPAWN_MARGIN)
        )
        return (x, y)
    
    def draw_boundaries(self, surface):
        """Draw boundary lines"""
        # Left wall (blue)
        pygame.draw.line(surface, config.BOUNDARY_COLORS['left_wall'],
                        (self.boundaries['left_wall'], 0),
                        (self.boundaries['left_wall'], self.screen_height), 3)
        
        # Right wall (blue)
        pygame.draw.line(surface, config.BOUNDARY_COLORS['right_wall'],
                        (self.boundaries['right_wall'], 0),
                        (self.boundaries['right_wall'], self.screen_height), 3)
        
        # Ceiling (yellow)
        pygame.draw.line(surface, config.BOUNDARY_COLORS['ceiling'],
                        (0, self.boundaries['ceiling']),
                        (self.screen_width, self.boundaries['ceiling']), 3)
        
        # Floor (green)
        pygame.draw.line(surface, config.BOUNDARY_COLORS['floor'],
                        (0, self.boundaries['floor']),
                        (self.screen_width, self.boundaries['floor']), 3) 