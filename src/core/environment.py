import pygame
import random

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
    
    def __init__(self, screen_width, screen_height, settings_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings_manager = settings_manager
        self.boundaries = self._calculate_boundaries()
        
        # Physics properties
        self.gravity = self.settings_manager.get_setting('physics.gravity', 0.5) if self.settings_manager else 0.5
        self.friction = self.settings_manager.get_setting('physics.friction', 0.95) if self.settings_manager else 0.95
        self.bounce_factor = self.settings_manager.get_setting('physics.bounce_factor', 0.7) if self.settings_manager else 0.7
        self.max_velocity = self.settings_manager.get_setting('physics.max_velocity', 10.0) if self.settings_manager else 10.0
        
        # Thrown physics properties
        self.thrown_max_velocity = self.settings_manager.get_setting('thrown_physics.max_velocity', 150.0) if self.settings_manager else 150.0
        self.thrown_min_velocity = self.settings_manager.get_setting('thrown_physics.min_throw_velocity', 50.0) if self.settings_manager else 50.0
        self.thrown_duration = self.settings_manager.get_setting('thrown_physics.throw_duration', 3.0) if self.settings_manager else 3.0
        self.thrown_bounce_loss = self.settings_manager.get_setting('thrown_physics.bounce_energy_loss', 0.7) if self.settings_manager else 0.7
        self.thrown_gravity_mult = self.settings_manager.get_setting('thrown_physics.gravity_multiplier', 1.5) if self.settings_manager else 1.5
        self.thrown_time_mult = self.settings_manager.get_setting('thrown_physics.time_multiplier', 60.0) if self.settings_manager else 60.0
        self.thrown_fallback_mult = self.settings_manager.get_setting('thrown_physics.fallback_multiplier', 2.0) if self.settings_manager else 2.0
        
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
    
    def update_boundaries(self):
        """Update boundaries from settings in realtime"""
        old_boundaries = self.boundaries.copy()
        self.boundaries = self._calculate_boundaries()
        
        # Log boundary changes
        if self.settings_manager:
            logger = self.settings_manager.get_logger() if hasattr(self.settings_manager, 'get_logger') else None
            if logger:
                logger.info(f"Boundaries updated: {old_boundaries} -> {self.boundaries}")
        
        return self.boundaries
    
    def _calculate_boundaries(self):
        """Calculate boundary positions from settings"""
        if not self.settings_manager:
            default_margin = 0.1
            return {
                'left_wall': int(self.screen_width * default_margin),
                'right_wall': int(self.screen_width * (1 - default_margin)),
                'ceiling': int(self.screen_height * default_margin),
                'floor': int(self.screen_height * (1 - default_margin))
            }
        
        # Get individual boundary settings
        floor_margin = self.settings_manager.get_setting('boundaries.floor_margin', 10) / 100.0
        ceiling_margin = self.settings_manager.get_setting('boundaries.ceiling_margin', 10) / 100.0
        wall_left_margin = self.settings_manager.get_setting('boundaries.wall_left_margin', 10) / 100.0
        wall_right_margin = self.settings_manager.get_setting('boundaries.wall_right_margin', 90) / 100.0
        
        return {
            'left_wall': int(self.screen_width * wall_left_margin),
            'right_wall': int(self.screen_width * wall_right_margin),
            'ceiling': int(self.screen_height * ceiling_margin),
            'floor': int(self.screen_height * (1 - floor_margin))
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
        """Get random position within boundaries - simple positioning"""
        safe_spawn_margin = self.settings_manager.get_setting('boundaries.safe_spawn_margin', 50) if self.settings_manager else 50
        
        # Simple positioning without anchor point consideration
        x = random.randint(
            self.boundaries['left_wall'] + safe_spawn_margin,
            max(self.boundaries['left_wall'] + safe_spawn_margin + 1, 
                self.boundaries['right_wall'] - pet_width - safe_spawn_margin)
        )
        y = random.randint(
            self.boundaries['ceiling'] + safe_spawn_margin,
            max(self.boundaries['ceiling'] + safe_spawn_margin + 1, 
                self.boundaries['floor'] - pet_height - safe_spawn_margin)
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
        # Walls - Original positioning
        self.surfaces['walls'] = [
            {'x': self.boundaries['left_wall'], 'y': 0, 'width': 10, 'height': self.screen_height, 'type': 'wall', 'side': 'left'},  # Left wall
            {'x': self.boundaries['right_wall'], 'y': 0, 'width': 10, 'height': self.screen_height, 'type': 'wall', 'side': 'right'}  # Right wall
        ]
        
        # Floors - Consistent positioning (floor thickness = 10px)
        self.surfaces['floors'] = [
            {'x': 0, 'y': self.boundaries['floor'], 'width': self.screen_width, 'height': 10, 'type': 'floor'}  # Bottom floor
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
        
        # Set position directly without boundary clamping interference
        pet.set_position(new_x, new_y)
    
    def _handle_physics_collisions(self, pet, new_x, new_y):
        """Handle physics-based collisions with bouncing"""
        pet_rect = pygame.Rect(new_x, new_y, pet.width, pet.height)
        
        # Check wall collisions with improved logic
        for wall in self.surfaces['walls']:
            wall_rect = pygame.Rect(wall['x'], wall['y'], wall['width'], wall['height'])
            if pet_rect.colliderect(wall_rect):
                if wall['side'] == 'right':  # Right wall
                    new_x = wall['x'] - pet.width
                    pet.velocity[0] = -pet.velocity[0] * self.bounce_factor
                elif wall['side'] == 'left':  # Left wall
                    new_x = wall['x']  # Place pet exactly at left wall boundary
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
        default_margin = self.settings_manager.get_setting('boundaries.default_margin', 0.1) if self.settings_manager else 0.1
        return {
            'left_wall': self.work_area['x'] + int(self.work_area['width'] * default_margin),
            'right_wall': self.work_area['x'] + int(self.work_area['width'] * (1 - default_margin)),
            'ceiling': self.work_area['y'] + int(self.work_area['height'] * default_margin),
            'floor': self.work_area['y'] + int(self.work_area['height'] * (1 - default_margin)),
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
    
    def draw(self, surface):
        """Draw all pets with anchor-based positioning"""
        for pet in self.pets:
            if pet.image:
                # Get correct draw position based on anchor point
                draw_x, draw_y = pet.get_draw_position()
                
                # Draw the pet at calculated position
                surface.blit(pet.image, (draw_x, draw_y))
                
                # Debug: Draw anchor point indicator
                if self.debug_mode:
                    anchor = pet.animation_manager.get_current_anchor()
                    if anchor:
                        # Draw anchor point as small red circle
                        pygame.draw.circle(surface, (255, 0, 0), 
                                        (pet.x, pet.y), 3)
                        
                        # Draw frame size rectangle
                        frame_w, frame_h = pet.get_frame_size()
                        pygame.draw.rect(surface, (0, 255, 0), 
                                       (draw_x, draw_y, frame_w, frame_h), 1)
    
    def draw_boundaries(self, surface):
        """Draw boundary lines"""
        # Get boundary colors from settings
        boundary_colors = self.settings_manager.get_setting('ui.boundary_colors', {
            'left_wall': [0, 0, 255],
            'right_wall': [0, 0, 255],
            'ceiling': [255, 255, 0],
            'floor': [0, 255, 0]
        }) if self.settings_manager else {
            'left_wall': [0, 0, 255],
            'right_wall': [0, 0, 255],
            'ceiling': [255, 255, 0],
            'floor': [0, 255, 0]
        }
        
        # Left wall (blue)
        pygame.draw.line(surface, boundary_colors['left_wall'],
                        (self.boundaries['left_wall'], 0),
                        (self.boundaries['left_wall'], self.screen_height), 3)
        
        # Right wall (blue)
        pygame.draw.line(surface, boundary_colors['right_wall'],
                        (self.boundaries['right_wall'], 0),
                        (self.boundaries['right_wall'], self.screen_height), 3)
        
        # Ceiling (yellow)
        pygame.draw.line(surface, boundary_colors['ceiling'],
                        (0, self.boundaries['ceiling']),
                        (self.screen_width, self.boundaries['ceiling']), 3)
        
        # Floor (green)
        pygame.draw.line(surface, boundary_colors['floor'],
                        (0, self.boundaries['floor']),
                        (self.screen_width, self.boundaries['floor']), 3)
    
    # ===== THROWN PHYSICS METHODS =====
    
    def calculate_throw_velocity(self, start_pos, end_pos, drag_time):
        """Calculate realistic throw velocity with time precision"""
        import math
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Time-based velocity (critical for realism)
        if drag_time > 0:
            vx = dx / drag_time * self.thrown_time_mult
            vy = dy / drag_time * self.thrown_time_mult
        else:
            # Fallback for instant release
            vx = dx * self.thrown_fallback_mult
            vy = dy * self.thrown_fallback_mult
        
        # Apply physics constraints
        velocity_magnitude = math.sqrt(vx**2 + vy**2)
        
        if velocity_magnitude > self.thrown_max_velocity:
            scale = self.thrown_max_velocity / velocity_magnitude
            vx *= scale
            vy *= scale
        
        return vx, vy
    
    def apply_thrown_physics(self, pet, delta_time):
        """Apply specialized physics for thrown pets"""
        if not pet.is_thrown:
            return
        
        # Update thrown timer
        pet.update_thrown_timer(delta_time)
        
        # Apply enhanced gravity to thrown velocity
        pet.thrown_velocity[1] += self.gravity * self.thrown_gravity_mult * delta_time
        
        # Update position
        current_x, current_y = pet.get_position()
        new_x = current_x + pet.thrown_velocity[0] * delta_time
        new_y = current_y + pet.thrown_velocity[1] * delta_time
        
        # Log thrown physics data for debugging
        from ..utils.log_manager import get_logger
        logger = get_logger("environment")
        logger.debug(f"Thrown physics - Timer: {pet.thrown_timer:.3f}s, Velocity: {pet.thrown_velocity}, Position: ({new_x:.1f}, {new_y:.1f})")
        
        # Handle collision
        if self.check_thrown_collision(pet, new_x, new_y):
            logger.debug("Thrown collision detected")
            self.handle_thrown_collision(pet)
        
        # Check if thrown state should end (Timer < 3 OR hit boundary)
        if (pet.thrown_timer >= self.thrown_duration or 
            self.check_boundary_collision(pet, new_x, new_y)):
            logger.debug(f"Ending thrown state - Timer: {pet.thrown_timer:.3f}s, Boundary hit: {self.check_boundary_collision(pet, new_x, new_y)}")
            self.end_thrown_state(pet)
        else:
            # Set new position
            pet.set_position(new_x, new_y)
    
    def check_thrown_collision(self, pet, new_x, new_y):
        """Check collision for thrown pets"""
        pet_rect = pygame.Rect(new_x, new_y, pet.width, pet.height)
        
        # Check all surfaces
        for surface_type, surfaces in self.surfaces.items():
            for surface in surfaces:
                surface_rect = pygame.Rect(surface['x'], surface['y'], surface['width'], surface['height'])
                if pet_rect.colliderect(surface_rect):
                    return True
        
        return False
    
    def handle_thrown_collision(self, pet):
        """Handle collision for thrown pets with energy loss"""
        # Apply bounce with energy loss
        pet.thrown_velocity[0] = -pet.thrown_velocity[0] * self.thrown_bounce_loss
        pet.thrown_velocity[1] = -pet.thrown_velocity[1] * self.thrown_bounce_loss
        
        # If velocity is too low, end thrown state
        velocity_magnitude = (pet.thrown_velocity[0]**2 + pet.thrown_velocity[1]**2)**0.5
        if velocity_magnitude < 5.0:  # Minimum velocity threshold
            self.end_thrown_state(pet)
    
    def check_boundary_collision(self, pet, new_x, new_y):
        """Check if pet hits boundary"""
        pet_rect = pygame.Rect(new_x, new_y, pet.width, pet.height)
        
        return (pet_rect.left < self.boundaries['left_wall'] or
                pet_rect.right > self.boundaries['right_wall'] or
                pet_rect.top < self.boundaries['ceiling'] or
                pet_rect.bottom > self.boundaries['floor'])
    
    def end_thrown_state(self, pet):
        """End thrown state and return to normal physics"""
        pet.end_thrown_state()
        # Reset to normal physics
        if not hasattr(pet, 'velocity'):
            pet.velocity = [0, 0]
        else:
            pet.velocity = [0, 0]  # Reset velocity 