import os
import pygame
import config
from .log_manager import get_logger

class AssetManager:
    """Handles asset loading and fallback creation"""
    
    @staticmethod
    def get_sprite_path():
        """Get sprite image path with fallback"""
        logger = get_logger("asset_manager")
        
        # Try multiple possible paths
        for path in config.POSSIBLE_SPRITE_PATHS:
            if os.path.exists(path):
                logger.asset_event("sprite", "found", path)
                return path
        
        logger.warning("No sprite image found, creating fallback...")
        return AssetManager._create_fallback_sprite()
    
    @staticmethod
    def _create_fallback_sprite():
        """Create fallback sprite if image not found"""
        logger = get_logger("asset_manager")
        logger.info("Creating fallback sprite...")
        
        fallback_surface = pygame.Surface(config.DEFAULT_SPRITE_SIZE)
        fallback_surface.fill((255, 100, 100))  # Light red square
        
        # Add some pattern to make it more interesting
        pygame.draw.circle(fallback_surface, (255, 255, 255), (32, 32), 20)
        pygame.draw.circle(fallback_surface, (0, 0, 0), (25, 25), 5)  # Left eye
        pygame.draw.circle(fallback_surface, (0, 0, 0), (39, 25), 5)  # Right eye
        pygame.draw.arc(fallback_surface, (0, 0, 0), (20, 35, 24, 12), 0, 3.14, 2)  # Smile
        
        fallback_path = config.FALLBACK_SPRITE_PATH
        pygame.image.save(fallback_surface, fallback_path)
        logger.asset_event("fallback_sprite", "created", fallback_path)
        return fallback_path 