import os
import pygame
import random
import sys

# Import our modular components
import config
from core.pet import Pet
from core.environment import Environment
from core.interaction import Interaction
from ui.pet_manager import PetManager
from ui.debug_manager import DebugManager
from ui.control_panel import ControlPanel
from utils.asset_manager import AssetManager
from utils.monitor_manager import MonitorManager
from utils.window_manager import WindowManager

# Optional Win32 imports with fallback
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️ Win32 modules not available. Using simple mode.")

# ========== MAIN APPLICATION WITH MODULAR ARCHITECTURE ==========
class DesktopPetApp:
    """Main application - orchestrates all modular systems with monitor awareness"""
    
    def __init__(self):
        self.running = False
        self.clock = None
        self.display = None
        self.transparent_mode = False
        self.monitor_info = None
        
        # Initialize modular systems
        self.pet_manager = PetManager()
        self.interaction = Interaction()
        self.environment = None
        self.debug_manager = DebugManager()
        self.control_panel = None  # Will be initialized after screen setup
        
    def initialize(self):
        """Initialize application with main monitor detection"""
        try:
            print("🚀 Initializing Desktop Pet...")
            
            # Initialize pygame
            pygame.init()
            self.clock = pygame.time.Clock()
            
            # Initialize debug manager font
            self.debug_manager.initialize_font()
            
            # Detect monitors and get main monitor info
            self.monitor_info = MonitorManager.get_main_monitor_info()
            all_monitors = MonitorManager.get_all_monitors()
            
            if len(all_monitors) > 1:
                print(f"🖥️ Multi-monitor setup detected. Using main monitor only.")
            
            # Try transparent window first, fall back to simple
            try:
                if WIN32_AVAILABLE:
                    self.display, hwnd, screen_width, screen_height = WindowManager.create_transparent_window(self.monitor_info)
                    self.transparent_mode = True
                    print("✅ Transparent mode enabled on main monitor")
                else:
                    raise ImportError("Win32 not available")
            except Exception as e:
                print(f"⚠️ Transparent mode failed: {e}")
                print("🔄 Falling back to simple mode...")
                self.display, hwnd, screen_width, screen_height = WindowManager.create_simple_window(self.monitor_info)
                self.transparent_mode = False
                print("✅ Simple mode enabled on main monitor")
            
            # Initialize environment
            self.environment = Environment(screen_width, screen_height)
            
            # Initialize control panel with screen dimensions
            self.control_panel = ControlPanel(screen_width, screen_height)
            
            # Load assets and create initial pets
            self._create_initial_pets()
            
            print("✅ Application initialized successfully!")
            self._print_controls()
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_initial_pets(self):
        """Create initial pets"""
        image_path = AssetManager.get_sprite_path()
        
        for i in range(config.INITIAL_SPRITE_COUNT):
            # Create pet at safe position
            temp_pet = Pet(image_path, 0, 0)  # Temporary for size
            try:
                safe_x, safe_y = self.environment.get_safe_spawn_position(
                    temp_pet.width, temp_pet.height
                )
            except:
                # Fallback position if boundary calculation fails
                safe_x, safe_y = 100 + i * 80, 100 + i * 60
            
            # Create actual pet at safe position
            pet = Pet(image_path, safe_x, safe_y)
            self.pet_manager.add_pet(pet)
        
        print(f"✅ Created {self.pet_manager.get_pet_count()} pets")
    
    def _print_controls(self):
        """Print control instructions"""
        print("\n🎮 Controls:")
        print("  WASD/Arrow Keys: Move selected pet")
        print("  Q/E: Switch pet selection")
        print("  SPACE: Add new pet")
        print("  DELETE/X: Remove selected pet")
        print("  F1: Toggle debug mode")
        print("  F2: Toggle control panel")  # NEW: Control panel toggle
        print("  ESC: Exit")
        print(f"\n🎨 Mode: {'Transparent' if self.transparent_mode else 'Simple Window'}")
        if self.monitor_info:
            print(f"🖥️ Monitor: {self.monitor_info['width']}x{self.monitor_info['height']} (Main)")
        print("🐛 Debug Features:")
        print("  🔵 Blue: Walls | 🟡 Yellow: Ceiling | 🟢 Green: Floor")
        print("  🟡 Yellow Box: Selected pet")
        print("  📊 FPS: Top-left corner")
        debug_status = "ON" if self.debug_manager.debug_mode else "OFF"
        print(f"  Current debug mode: {debug_status}")
        print("🎛️ Control Panel:")
        print("  F2: Show/Hide control panel")
        print("  Mouse: Click tabs and buttons")
        print("  Tabs: Pets, Settings, TikTok, Logs")
    
    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_F1:
                    self.debug_manager.toggle_debug_mode()
                
                elif event.key == pygame.K_F2:  # NEW: Control panel toggle
                    self.control_panel.toggle_visibility()
                    status = "shown" if self.control_panel.visible else "hidden"
                    print(f"🎛️ Control panel {status}")
                
                elif event.key == pygame.K_q:
                    self.pet_manager.select_previous()
                    print(f"Selected pet #{self.pet_manager.selected_index + 1}")
                
                elif event.key == pygame.K_e:
                    self.pet_manager.select_next()
                    print(f"Selected pet #{self.pet_manager.selected_index + 1}")
                
                elif event.key == pygame.K_SPACE:
                    self._add_new_pet()
                
                elif event.key == pygame.K_DELETE or event.key == pygame.K_x:
                    self._remove_selected_pet()
            
            # Handle control panel input
            if self.control_panel.visible:
                action = self.control_panel.handle_input(event)
                if action:
                    self._handle_control_panel_action(action)
    
    def _handle_control_panel_action(self, action):
        """Handle control panel button actions"""
        if action == 'add_pet':
            self._add_new_pet()
            print("🎛️ Added pet via control panel")
        
        elif action == 'remove_pet':
            self._remove_selected_pet()
            print("🎛️ Removed pet via control panel")
        
        elif action == 'clear_all':
            self._clear_all_pets()
            print("🎛️ Cleared all pets via control panel")
        
        elif action == 'toggle_debug':
            self.debug_manager.toggle_debug_mode()
            print("🎛️ Toggled debug mode via control panel")
        
        elif action == 'toggle_boundaries':
            # This would toggle boundary visibility
            print("🎛️ Toggled boundaries via control panel")
        
        elif action == 'connect_tiktok':
            print("🎛️ TikTok connect button pressed")
        
        elif action == 'disconnect_tiktok':
            print("🎛️ TikTok disconnect button pressed")
    
    def _add_new_pet(self):
        """Add new pet at safe position"""
        try:
            image_path = AssetManager.get_sprite_path()
            temp_pet = Pet(image_path, 0, 0)
            try:
                safe_x, safe_y = self.environment.get_safe_spawn_position(
                    temp_pet.width, temp_pet.height
                )
            except:
                # Fallback position
                safe_x, safe_y = random.randint(100, 400), random.randint(100, 300)
            
            new_pet = Pet(image_path, safe_x, safe_y)
            self.pet_manager.add_pet(new_pet)
            print(f"➕ Added pet #{self.pet_manager.get_pet_count()}")
        
        except Exception as e:
            print(f"❌ Error adding pet: {e}")
    
    def _remove_selected_pet(self):
        """Remove selected pet"""
        if self.pet_manager.get_pet_count() > 1:  # Keep at least one pet
            self.pet_manager.remove_selected_pet()
            print(f"➖ Removed pet. Remaining: {self.pet_manager.get_pet_count()}")
        else:
            print("⚠️ Cannot remove last pet!")
    
    def _clear_all_pets(self):
        """Clear all pets and create one new pet"""
        self.pet_manager.pets.clear()
        self.pet_manager.selected_index = 0
        self._add_new_pet()
        print("🗑️ Cleared all pets and created new one")
    
    def update(self):
        """Update game logic"""
        # Update FPS counter
        self.debug_manager.update_fps(self.clock)
        
        # Get movement input (only if control panel is not visible)
        if not self.control_panel.visible:
            keys = pygame.key.get_pressed()
            dx, dy = self.interaction.get_movement_from_input(keys)
            
            # Apply movement to selected pet
            if dx != 0 or dy != 0:
                selected = self.pet_manager.get_selected_pet()
                if selected:
                    self.interaction.apply_movement(selected, dx, dy)
                    if self.environment:
                        self.environment.clamp_position(selected)
    
    def render(self):
        """Render everything"""
        # Clear with black (transparent in transparent mode)
        if self.transparent_mode:
            self.display.fill(config.TRANSPARENT_BG)  # Black = transparent
        else:
            self.display.fill(config.SIMPLE_BG)  # Dark gray background
        
        # Draw boundaries ONLY in debug mode
        if self.debug_manager.should_show_boundaries() and self.environment:
            self.environment.draw_boundaries(self.display)
        
        # Draw all pets
        self.pet_manager.draw_all(self.display)
        
        # Draw selection indicator ONLY in debug mode
        if self.debug_manager.should_show_selection_box():
            self.pet_manager.draw_selection_indicator(self.display)
        
        # Draw debug info (FPS) in top-left corner
        self.debug_manager.draw_debug_info(self.display)
        
        # Draw info text (only in simple mode and debug mode)
        if not self.transparent_mode and self.debug_manager.debug_mode:
            font = pygame.font.Font(None, config.INFO_FONT_SIZE)
            info_text = f"Pet {self.pet_manager.selected_index + 1}/{self.pet_manager.get_pet_count()}"
            text_surface = font.render(info_text, True, config.INFO_TEXT_COLOR)
            self.display.blit(text_surface, (10, 40))  # Moved down to avoid FPS overlap
            
            # Show monitor info
            if self.monitor_info:
                monitor_text = f"Main Monitor: {self.monitor_info['width']}x{self.monitor_info['height']}"
                monitor_surface = font.render(monitor_text, True, config.MONITOR_INFO_COLOR)
                self.display.blit(monitor_surface, (10, 65))
            
            # Show control panel hint
            if not self.control_panel.visible:
                hint_text = "Press F2 for Control Panel"
                hint_surface = font.render(hint_text, True, (150, 150, 150))
                self.display.blit(hint_surface, (10, 90))
        
        # Draw control panel (on top of everything)
        self.control_panel.render(self.display)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            print("❌ Failed to initialize. Exiting...")
            return
        
        print("🎮 Desktop Pet is running on main monitor! Use controls to interact.")
        self.running = True
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(config.FPS_TARGET)  # 60 FPS
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("🏁 Desktop Pet closing...")
            pygame.quit()
            sys.exit()

# ========== ENTRY POINT ==========
def main():
    """Main entry point"""
    print("🌟 Starting Desktop Pet Application")
    print("📋 Dependencies check:")
    print(f"   - pygame: {'✅' if 'pygame' in sys.modules else '❌'}")
    print(f"   - win32: {'✅' if WIN32_AVAILABLE else '❌ (fallback to simple mode)'}")
    
    app = DesktopPetApp()
    app.run()

if __name__ == "__main__":
    main() 