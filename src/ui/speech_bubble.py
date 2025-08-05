# Speech Bubble for Desktop Pet Application
# This module will handle text bubble rendering

class SpeechBubble:
    """Text bubble rendering system for pet communication"""
    
    def __init__(self):
        self.text = ""
        self.timer = 0
        self.duration = 10  # seconds
        self.visible = False
    
    def show_text(self, text, duration=10):
        """Show text in speech bubble"""
        self.text = text
        self.timer = duration
        self.visible = True
    
    def update(self, delta_time):
        """Update speech bubble timer"""
        if self.visible:
            self.timer -= delta_time
            if self.timer <= 0:
                self.visible = False
    
    def render(self, surface, position):
        """Render speech bubble at position"""
        # TODO: Implement speech bubble rendering
        pass 