# UI Manager for Desktop Pet Application
# Simplified version - only keeps what's actually used

import pygame
from typing import Dict, Optional
from ..utils.log_manager import get_logger

class UIManager:
    """Simplified UI management system - only keeps used functionality"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.logger = get_logger("ui_manager")
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.logger.info(f"UIManager initialized for {screen_width}x{screen_height}")
    
    def render_game_screen(self, surface, game_state):
        """Render complete game screen with all elements"""
        # Clear with appropriate background
        if game_state.get('transparent_mode', False):
            surface.fill((0, 0, 0))  # Black = transparent
        else:
            surface.fill((30, 30, 30))  # Dark gray background
        
        # Render game elements in order
        self._render_boundaries(surface, game_state)
        self._render_pets(surface, game_state)
        self._render_pet_debug_info(surface, game_state)
        self._render_selection(surface, game_state)
        self._render_debug_info(surface, game_state)
        self._render_control_panel(surface, game_state)
        
        # Update display
        pygame.display.flip()
    
    def _render_boundaries(self, surface, game_state):
        """Render boundaries if debug mode is enabled"""
        debug_manager = game_state.get('debug_manager')
        environment = game_state.get('environment')
        
        if debug_manager and environment and debug_manager.should_show_boundaries():
            environment.draw_boundaries(surface)
    
    def _render_pets(self, surface, game_state):
        """Render all pets"""
        pet_manager = game_state.get('pet_manager')
        if pet_manager:
            pet_manager.draw_all(surface)
    
    def _render_pet_debug_info(self, surface, game_state):
        """Render debug info for each pet"""
        debug_manager = game_state.get('debug_manager')
        pet_manager = game_state.get('pet_manager')
        
        if debug_manager and pet_manager and debug_manager.debug_mode:
            for i, pet in enumerate(pet_manager.pets):
                debug_manager.draw_pet_debug_info(surface, pet, i)
    
    def _render_selection(self, surface, game_state):
        """Render selection indicator if debug mode is enabled"""
        debug_manager = game_state.get('debug_manager')
        pet_manager = game_state.get('pet_manager')
        
        if debug_manager and pet_manager and debug_manager.should_show_selection_box():
            pet_manager.draw_selection_indicator(surface)
    
    def _render_debug_info(self, surface, game_state):
        """Render debug information"""
        debug_manager = game_state.get('debug_manager')
        if debug_manager:
            debug_manager.draw_debug_info(surface)
    
    def _render_control_panel(self, surface, game_state):
        """Render control panel"""
        control_panel = game_state.get('control_panel')
        if control_panel:
            control_panel.render(surface) 