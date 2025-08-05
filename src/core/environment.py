import pygame
import random
import config

# Optional Win32 imports with fallback
try:
    import win32gui
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ Win32 modules not available. Using fallback environment detection.")

class Environment:
    """Handles all boundary-related logic, virtual environment detection, and physics"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.boundaries = self._calculate_boundaries()
        
        # Physics properties
        self.gravity = 0.5
        self.friction = 0.95
        self.bounce_factor = 0.7
        self.max_velocity = 10.0
        
        # Virtual boundary detection
        self.taskbar_height = self._detect_taskbar_height()
        self.work_area = self._get_work_area()
        
        # Surface detection
        self.surfaces = {
            'walls': [],
            'floors': [],
            'ceilings': [],
            'platforms': []
        }
        self._initialize_surfaces()
    
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
    
    def _detect_taskbar_height(self):
        """Detect Windows taskbar height"""
        if not WIN32_AVAILABLE:
            return 40  # Default taskbar height
        
        try:
            # Get work area vs screen area
            work_area = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
            screen_area = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
            
            # Calculate taskbar height
            taskbar_height = screen_area[1] - (work_area[3] - work_area[1])
            return max(0, taskbar_height)
        except:
            return 40  # Default taskbar height
    
    def _get_work_area(self):
        """Get actual work area (screen minus taskbar)"""
        if not WIN32_AVAILABLE:
            return {
                'x': 0,
                'y': 0,
                'width': self.screen_width,
                'height': self.screen_height - self.taskbar_height
            }
        
        try:
            work_area = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
            return {
                'x': work_area[0],
                'y': work_area[1],
                'width': work_area[2] - work_area[0],
                'height': work_area[3] - work_area[1]
            }
        except:
            return {
                'x': 0,
                'y': 0,
                'width': self.screen_width,
                'height': self.screen_height - self.taskbar_height
            }
    
    def _initialize_surfaces(self):
        """Initialize virtual surfaces for physics using boundary positions"""
        # Use boundary positions for consistent collision detection
        # Walls
        self.surfaces['walls'] = [
            {'x': self.boundaries['left_wall'], 'y': 0, 'width': 10, 'height': self.screen_height, 'type': 'wall'},  # Left wall
            {'x': self.boundaries['right_wall'] - 10, 'y': 0, 'width': 10, 'height': self.screen_height, 'type': 'wall'}  # Right wall
        ]
        
        # Floors
        self.surfaces['floors'] = [
            {'x': 0, 'y': self.boundaries['floor'] - 10, 'width': self.screen_width, 'height': 10, 'type': 'floor'}  # Bottom floor
        ]
        
        # Ceilings
        self.surfaces['ceilings'] = [
            {'x': 0, 'y': self.boundaries['ceiling'], 'width': self.screen_width, 'height': 10, 'type': 'ceiling'}  # Top ceiling
        ]
    
    def apply_physics(self, pet, delta_time, user_moving=False):
        """Apply physics to pet (gravity, friction, bouncing)"""
        if not hasattr(pet, 'velocity'):
            pet.velocity = [0, 0]
        
        # If user is moving the pet, reset velocity to prevent physics interference
        if user_moving:
            pet.velocity = [0, 0]
            return
        
        # Apply gravity
        pet.velocity[1] += self.gravity
        
        # Apply friction
        pet.velocity[0] *= self.friction
        pet.velocity[1] *= self.friction
        
        # Clamp velocity
        pet.velocity[0] = max(-self.max_velocity, min(self.max_velocity, pet.velocity[0]))
        pet.velocity[1] = max(-self.max_velocity, min(self.max_velocity, pet.velocity[1]))
        
        # Apply velocity to position
        current_x, current_y = pet.get_position()
        new_x = current_x + pet.velocity[0]
        new_y = current_y + pet.velocity[1]
        
        # Check collisions and apply bouncing
        new_x, new_y = self._handle_physics_collisions(pet, new_x, new_y)
        
        pet.set_position(new_x, new_y)
    
    def _handle_physics_collisions(self, pet, new_x, new_y):
        """Handle physics-based collisions with bouncing"""
        pet_rect = pygame.Rect(new_x, new_y, pet.width, pet.height)
        
        # Check wall collisions
        for wall in self.surfaces['walls']:
            wall_rect = pygame.Rect(wall['x'], wall['y'], wall['width'], wall['height'])
            if pet_rect.colliderect(wall_rect):
                if wall['x'] < pet_rect.centerx:  # Right wall
                    new_x = wall['x'] - pet.width
                    pet.velocity[0] = -pet.velocity[0] * self.bounce_factor
                else:  # Left wall
                    new_x = wall['x'] + wall['width']
                    pet.velocity[0] = -pet.velocity[0] * self.bounce_factor
        
        # Check floor/ceiling collisions
        for surface in self.surfaces['floors'] + self.surfaces['ceilings']:
            surface_rect = pygame.Rect(surface['x'], surface['y'], surface['width'], surface['height'])
            if pet_rect.colliderect(surface_rect):
                if surface['type'] == 'floor':  # Floor collision
                    new_y = surface['y'] - pet.height
                    # Stop falling when hitting floor
                    if pet.velocity[1] > 0:  # Only if falling down
                        pet.velocity[1] = -pet.velocity[1] * self.bounce_factor
                        # If bounce is too small, stop bouncing
                        if abs(pet.velocity[1]) < 1.0:
                            pet.velocity[1] = 0
                elif surface['type'] == 'ceiling':  # Ceiling collision
                    new_y = surface['y'] + surface['height']
                    pet.velocity[1] = -pet.velocity[1] * self.bounce_factor
        
        return new_x, new_y
    
    def get_virtual_boundaries(self):
        """Get virtual boundaries considering taskbar and work area"""
        return {
            'left_wall': self.work_area['x'] + int(self.work_area['width'] * config.DEFAULT_BOUNDARY_MARGIN),
            'right_wall': self.work_area['x'] + int(self.work_area['width'] * (1 - config.DEFAULT_BOUNDARY_MARGIN)),
            'ceiling': self.work_area['y'] + int(self.work_area['height'] * config.DEFAULT_BOUNDARY_MARGIN),
            'floor': self.work_area['y'] + int(self.work_area['height'] * (1 - config.DEFAULT_BOUNDARY_MARGIN)),
            'taskbar_height': self.taskbar_height,
            'work_area': self.work_area
        }
    
    def check_surface_collision(self, pet):
        """Check if pet is on a surface (for climbing mechanics)"""
        pet_rect = pet.get_rect()
        
        for surface_type, surfaces in self.surfaces.items():
            for surface in surfaces:
                surface_rect = pygame.Rect(surface['x'], surface['y'], surface['width'], surface['height'])
                if pet_rect.colliderect(surface_rect):
                    return {
                        'type': surface['type'],
                        'surface': surface,
                        'collision': True
                    }
        
        return {'collision': False}
    
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