import pygame
from ..core.pet import Pet
from .sprite_name_chat import SpriteNameChat

class PetManager:
    """Manages collection of pets with text rendering"""
    
    def __init__(self):
        self.pets = []
        self.selected_index = 0
        self.sprite_name_chat = SpriteNameChat()
    
    def add_pet(self, pet=None):
        """Add pet to collection"""
        if pet is None:
            # Create default pet if none provided
            # This will be handled by the calling code
            return len(self.pets)
        self.pets.append(pet)
        return len(self.pets) - 1
    
    def remove_pet(self, index):
        """Remove pet by index"""
        if 0 <= index < len(self.pets):
            self.pets.pop(index)
            self._update_selection()
    
    def remove_selected_pet(self):
        """Remove currently selected pet"""
        if self.pets:
            self.remove_pet(self.selected_index)
    
    def get_selected_pet(self):
        """Get currently selected pet"""
        if self.pets and 0 <= self.selected_index < len(self.pets):
            return self.pets[self.selected_index]
        return None
    
    def select_next(self):
        """Select next pet"""
        if self.pets:
            self.selected_index = (self.selected_index + 1) % len(self.pets)
    
    def select_previous(self):
        """Select previous pet"""
        if self.pets:
            self.selected_index = (self.selected_index - 1) % len(self.pets)
    
    def _update_selection(self):
        """Update selection after pet removal"""
        if not self.pets:
            self.selected_index = 0
        elif self.selected_index >= len(self.pets):
            self.selected_index = len(self.pets) - 1
    
    def get_pet_count(self):
        """Get number of pets"""
        return len(self.pets)
    
    def clear_all_pets(self):
        """Clear all pets from collection"""
        self.pets.clear()
        self.selected_index = 0
    
    def draw_all(self, surface):
        """Draw all pets with names and chat bubbles"""
        for pet in self.pets:
            # Draw pet sprite
            pet.draw(surface)
            
            # Draw name and chat
            self.sprite_name_chat.render_pet_text(surface, pet, pet.get_name(), pet.get_chat())
    
    def draw_selection_indicator(self, surface):
        """Draw selection indicator around selected pet"""
        selected = self.get_selected_pet()
        if selected:
            rect = selected.get_rect()
            selection_color = (255, 255, 0)  # Yellow selection color
            selection_thickness = 2  # Selection thickness
            pygame.draw.rect(surface, selection_color, rect, selection_thickness) 