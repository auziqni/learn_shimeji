# UI Manager for Desktop Pet Application
# This module handles UI rendering and management with layer system

import pygame
from typing import Dict, List, Optional
from ..utils.log_manager import get_logger

class UIManager:
    """Centralized UI management system with layer-based rendering"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.logger = get_logger("ui_manager")
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Layer-based UI organization
        self.layers = {
            'background': [],  # Background elements (walls, floors)
            'game': [],        # Game objects (pets, boundaries)
            'ui': [],          # UI elements (buttons, panels)
            'overlay': []      # Overlay elements (debug info, notifications)
        }
        
        # UI state management
        self.active_panels = []
        self.focused_element = None
        self.hovered_element = None
        
        # Rendering state
        self.dirty_regions = []  # Areas that need re-rendering
        self.last_render_time = 0
        
        self.logger.info(f"UIManager initialized for {screen_width}x{screen_height}")
    
    def add_to_layer(self, element, layer_name: str):
        """Add UI element to specific layer"""
        if layer_name not in self.layers:
            self.logger.warning(f"Unknown layer: {layer_name}")
            layer_name = 'ui'  # Default to UI layer
        
        self.layers[layer_name].append(element)
        self.logger.debug(f"Added element to {layer_name} layer")
    
    def remove_from_layer(self, element, layer_name: str):
        """Remove UI element from specific layer"""
        if layer_name in self.layers and element in self.layers[layer_name]:
            self.layers[layer_name].remove(element)
            self.logger.debug(f"Removed element from {layer_name} layer")
    
    def render_all_layers(self, surface):
        """Render all layers in proper order"""
        # Clear surface with appropriate background
        self._clear_background(surface)
        
        # Render layers in order
        for layer_name in ['background', 'game', 'ui', 'overlay']:
            for element in self.layers[layer_name]:
                if hasattr(element, 'visible') and not element.visible:
                    continue
                if hasattr(element, 'render'):
                    element.render(surface)
        
        # Update display
        pygame.display.flip()
    
    def _clear_background(self, surface):
        """Clear surface with appropriate background"""
        # This will be overridden by game state
        surface.fill((0, 0, 0))  # Default black background
    
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
    
    def handle_ui_events(self, event):
        """Handle UI events with proper propagation"""
        # Handle events in reverse layer order (overlay first)
        for layer_name in reversed(['overlay', 'ui', 'game', 'background']):
            for element in self.layers[layer_name]:
                if hasattr(element, 'handle_event') and element.handle_event(event):
                    return True  # Event handled, stop propagation
        
        return False
    
    def update_hover_states(self):
        """Update hover states for all UI elements"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Check hover states in reverse layer order
        for layer_name in reversed(['overlay', 'ui', 'game', 'background']):
            for element in self.layers[layer_name]:
                if hasattr(element, 'update_hover_state'):
                    element.update_hover_state(mouse_pos)
    
    def get_layer_info(self) -> Dict[str, int]:
        """Get information about layers"""
        return {layer: len(elements) for layer, elements in self.layers.items()}
    
    def clear_layer(self, layer_name: str):
        """Clear all elements from a specific layer"""
        if layer_name in self.layers:
            self.layers[layer_name].clear()
            self.logger.info(f"Cleared {layer_name} layer")
    
    def clear_all_layers(self):
        """Clear all layers"""
        for layer_name in self.layers:
            self.layers[layer_name].clear()
        self.logger.info("Cleared all UI layers") 