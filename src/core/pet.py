import pygame
import config

class Pet:
    """Individual pet entity - handles image and position data"""
    
    def __init__(self, image_path, x=0, y=0):
        try:
            self.image = pygame.image.load(image_path)
        except pygame.error as e:
            print(f"⚠️ Could not load image {image_path}: {e}")
            # Create fallback red square
            self.image = pygame.Surface(config.DEFAULT_SPRITE_SIZE)
            self.image.fill(config.FALLBACK_SPRITE_COLOR)
        
        self.x = x
        self.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def get_rect(self):
        """Get pygame rect for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def set_position(self, x, y):
        """Set pet position"""
        self.x = x
        self.y = y
    
    def get_position(self):
        """Get pet position"""
        return (self.x, self.y)
    
    def draw(self, surface):
        """Draw pet to surface"""
        surface.blit(self.image, (self.x, self.y)) 