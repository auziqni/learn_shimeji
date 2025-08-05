import pygame
import config
from core.pet import Pet

class PetManager:
    """Manages collection of pets"""
    
    def __init__(self):
        self.pets = []
        self.selected_index = 0
    
    def add_pet(self, pet):
        """Add pet to collection"""
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
    
    def draw_all(self, surface):
        """Draw all pets"""
        for pet in self.pets:
            pet.draw(surface)
    
    def draw_selection_indicator(self, surface):
        """Draw selection indicator around selected pet"""
        selected = self.get_selected_pet()
        if selected:
            rect = selected.get_rect()
            pygame.draw.rect(surface, config.SELECTION_COLOR, rect, config.SELECTION_THICKNESS) 