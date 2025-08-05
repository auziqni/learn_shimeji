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
from ui.ui_manager import UIManager
from utils.asset_manager import AssetManager
from utils.monitor_manager import MonitorManager
from utils.window_manager import WindowManager
from utils.log_manager import get_logger
from utils.json_parser import JSONParser

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
        # Initialize logger first
        self.logger = get_logger("main")
        self.logger.info("Initializing Desktop Pet Application")
        
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
        
        # Initialize JSONParser for sprite packs
        self.json_parser = None
        
    def initialize(self):
        """Initialize application with main monitor detection"""
        try:
            self.logger.info("Starting application initialization")
            
            # Initialize pygame
            pygame.init()
            self.clock = pygame.time.Clock()
            self.logger.debug("Pygame initialized successfully")
            
            # Initialize debug manager font
            self.debug_manager.initialize_font()
            
            # Detect monitors and get main monitor info
            self.monitor_info = MonitorManager.get_main_monitor_info()
            all_monitors = MonitorManager.get_all_monitors()
            
            if len(all_monitors) > 1:
                self.logger.info(f"Multi-monitor setup detected ({len(all_monitors)} monitors). Using main monitor only.")
            
            # Try transparent window first, fall back to simple
            try:
                if WIN32_AVAILABLE:
                    self.display, hwnd, screen_width, screen_height = WindowManager.create_transparent_window(self.monitor_info)
                    self.transparent_mode = True
                    self.logger.info("Transparent mode enabled on main monitor")
                else:
                    raise ImportError("Win32 not available")
            except Exception as e:
                self.logger.warning(f"Transparent mode failed: {e}")
                self.logger.info("Falling back to simple mode...")
                self.display, hwnd, screen_width, screen_height = WindowManager.create_simple_window(self.monitor_info)
                self.transparent_mode = False
                self.logger.info("Simple mode enabled on main monitor")
            
            # Initialize environment
            self.environment = Environment(screen_width, screen_height)
            
            # Initialize control panel with screen dimensions
            self.control_panel = ControlPanel(screen_width, screen_height)
            
            # Initialize UI Manager
            self.ui_manager = UIManager(screen_width, screen_height)
            
            # Initialize JSONParser and load sprite packs
            if not self._initialize_sprite_packs():
                self.logger.critical("Failed to initialize sprite packs")
                return False
            
            # Load assets and create initial pets
            self._create_initial_pets()
            
            self.logger.info("Application initialized successfully!")
            self._print_controls()
            
            return True
            
        except Exception as e:
            self.logger.exception(f"Initialization failed: {e}")
            return False
    
    def _create_initial_pets(self):
        """Create initial pets with Hornet sprite"""
        for i in range(config.INITIAL_SPRITE_COUNT):
            try:
                # Create pet at safe position
                temp_pet = Pet(0, 0, "Hornet", self.json_parser)  # Temporary for size
                try:
                    safe_x, safe_y = self.environment.get_safe_spawn_position(
                        temp_pet.width, temp_pet.height
                    )
                except:
                    # Fallback position if boundary calculation fails
                    safe_x, safe_y = 100 + i * 80, 100 + i * 60
                
                # Create actual pet at safe position
                pet = Pet(safe_x, safe_y, "Hornet", self.json_parser)
                self.pet_manager.add_pet(pet)
                
            except Exception as e:
                self.logger.error(f"Failed to create pet #{i+1}: {e}")
                # Create fallback pet
                fallback_pet = Pet(100 + i * 80, 100 + i * 60, "Hornet")
                self.pet_manager.add_pet(fallback_pet)
        
        self.logger.info(f"Created {self.pet_manager.get_pet_count()} initial pets")
    
    def _initialize_sprite_packs(self):
        """Initialize JSONParser and load sprite packs"""
        try:
            self.logger.info("Initializing sprite packs...")
            
            # Initialize JSONParser
            self.json_parser = JSONParser(assets_dir="assets", quiet_warnings=False, more_data_show=True)
            
            # Load all sprite packs
            sprite_status = self.json_parser.load_all_sprite_packs()
            
            # Check if Hornet is available and ready
            if "Hornet" not in sprite_status:
                self.logger.error("Hornet sprite pack not found")
                return False
            
            hornet_status = sprite_status["Hornet"]
            if hornet_status != "READY":
                self.logger.error(f"Hornet sprite pack not ready: {hornet_status}")
                return False
            
            self.logger.info("Sprite packs initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize sprite packs: {e}")
            return False
    
    def _print_controls(self):
        """Print control instructions"""
        self.logger.info("Application Controls:")
        self.logger.info("  WASD: Move selected pet")
        self.logger.info("  Q/E: Switch pet selection")
        self.logger.info("  UP/DOWN Arrow: Previous/Next sprite pack")
        self.logger.info("  LEFT/RIGHT Arrow: Previous/Next action type")
        self.logger.info("  Z/C: Previous/Next action")
        self.logger.info("  M: Toggle sound")
        self.logger.info("  +/-: Volume up/down")
        self.logger.info("  SPACE: Add new pet")
        self.logger.info("  DELETE/X: Remove selected pet")
        self.logger.info("  F1: Toggle debug mode")
        self.logger.info("  F2: Toggle control panel")
        self.logger.info("  ESC: Exit")
        
        mode = 'Transparent' if self.transparent_mode else 'Simple Window'
        self.logger.info(f"Mode: {mode}")
        
        if self.monitor_info:
            self.logger.info(f"Monitor: {self.monitor_info['width']}x{self.monitor_info['height']} (Main)")
        
        debug_status = "ON" if self.debug_manager.debug_mode else "OFF"
        self.logger.info(f"Debug mode: {debug_status}")
        
        # Also print to console for user visibility
        print("\n🎮 Controls:")
        print("  WASD: Move selected pet")
        print("  Q/E: Switch pet selection")
        print("  UP/DOWN Arrow: Previous/Next sprite pack")
        print("  LEFT/RIGHT Arrow: Previous/Next action type")
        print("  Z/C: Previous/Next action")
        print("  M: Toggle sound")
        print("  +/-: Volume up/down")
        print("  SPACE: Add new pet")
        print("  DELETE/X: Remove selected pet")
        print("  F1: Toggle debug mode")
        print("  F2: Toggle control panel")
        print("  ESC: Exit")
        print(f"\n🎨 Mode: {mode}")
        if self.monitor_info:
            print(f"🖥️ Monitor: {self.monitor_info['width']}x{self.monitor_info['height']} (Main)")
        print("🐛 Debug Features:")
        print("  🔵 Blue: Walls | 🟡 Yellow: Ceiling | 🟢 Green: Floor")
        print("  🟡 Yellow Box: Selected pet")
        print("  📊 FPS: Top-left corner")
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
            
            # Delegate keyboard events to Interaction class
            elif event.type == pygame.KEYDOWN:
                # Create app state dictionary for interaction
                app_state = {
                    'running': self.running,
                    'logger': self.logger,
                    'pet_manager': self.pet_manager,
                    'debug_manager': self.debug_manager,
                    'control_panel': self.control_panel,
                    'json_parser': self.json_parser
                }
                
                # Handle keyboard events through Interaction
                if self.interaction.handle_keyboard_events(event, app_state):
                    # Update running state if it was changed
                    self.running = app_state['running']
                    continue
            
            # Handle control panel input
            if self.control_panel.visible:
                action = self.control_panel.handle_input(event)
                if action:
                    self._handle_control_panel_action(action)
    
    def _handle_control_panel_action(self, action):
        """Handle actions from control panel"""
        if action == "add_pet":
            self._add_new_pet()
        elif action == "remove_pet":
            self._remove_selected_pet()
        elif action == "clear_pets":
            self._clear_all_pets()
        elif action == "toggle_debug":
            self.debug_manager.toggle_debug_mode()
        elif action == "toggle_boundaries":
            self.debug_manager.toggle_boundaries()
        elif action == "toggle_selection":
            self.debug_manager.toggle_selection_box()
        else:
            self.logger.warning(f"Unknown control panel action: {action}")
    
    def _add_new_pet(self):
        """Add new pet to the scene"""
        self.pet_manager.add_pet()
        pet_count = self.pet_manager.get_pet_count()
        self.logger.user_action("add_pet", f"Added pet #{pet_count}")
        print(f"➕ Added pet #{pet_count}")
    
    def _remove_selected_pet(self):
        """Remove selected pet from the scene"""
        if self.pet_manager.get_pet_count() > 1:
            self.pet_manager.remove_selected_pet()
            self.logger.user_action("remove_pet", "Removed selected pet")
            print("➖ Removed selected pet")
        else:
            self.logger.warning("Cannot remove last pet")
            print("⚠️ Cannot remove last pet")
    
    def _clear_all_pets(self):
        """Clear all pets from the scene"""
        self.pet_manager.clear_all_pets()
        self.logger.user_action("clear_pets", "Cleared all pets")
        print("🗑️ Cleared all pets")
    
    def update(self):
        """Update game logic"""
        # Update FPS counter
        self.debug_manager.update_fps(self.clock)
        
        # Update animations for all pets
        delta_time = self.clock.get_time() / 1000.0  # Convert to seconds
        for pet in self.pet_manager.pets:
            pet.update_animation(delta_time)
        
        # Update pet movement through Interaction class
        self.interaction.update_pet_movement(
            self.pet_manager, 
            self.environment, 
            self.control_panel.visible
        )
    
    def render(self):
        """Render everything using UI Manager"""
        # Create game state dictionary for UI Manager
        game_state = {
            'transparent_mode': self.transparent_mode,
            'debug_manager': self.debug_manager,
            'environment': self.environment,
            'pet_manager': self.pet_manager,
            'control_panel': self.control_panel,
            'monitor_info': self.monitor_info
        }
        
        # Use UI Manager to render the complete game screen
        self.ui_manager.render_game_screen(self.display, game_state)
        
        # Draw additional info text (only in simple mode and debug mode)
        if not self.transparent_mode and self.debug_manager.debug_mode:
            self._render_additional_info()
    
    def _render_additional_info(self):
        """Render additional debug information"""
        font = pygame.font.Font(None, config.INFO_FONT_SIZE)
        
        # Pet info
        info_text = f"Pet {self.pet_manager.selected_index + 1}/{self.pet_manager.get_pet_count()}"
        text_surface = font.render(info_text, True, config.INFO_TEXT_COLOR)
        self.display.blit(text_surface, (10, 40))  # Moved down to avoid FPS overlap
        
        # Monitor info
        if self.monitor_info:
            monitor_text = f"Main Monitor: {self.monitor_info['width']}x{self.monitor_info['height']}"
            monitor_surface = font.render(monitor_text, True, config.MONITOR_INFO_COLOR)
            self.display.blit(monitor_surface, (10, 65))
        
        # Control panel hint
        if not self.control_panel.visible:
            hint_text = "Press F2 for Control Panel"
            hint_surface = font.render(hint_text, True, (150, 150, 150))
            self.display.blit(hint_surface, (10, 90))
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            self.logger.critical("Failed to initialize. Exiting...")
            print("❌ Failed to initialize. Exiting...")
            return
        
        self.logger.info("Desktop Pet is running on main monitor! Use controls to interact.")
        print("🎮 Desktop Pet is running on main monitor! Use controls to interact.")
        self.running = True
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(config.FPS_TARGET)  # 60 FPS
        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            print("\n⚠️ Interrupted by user")
        except Exception as e:
            self.logger.exception(f"Runtime error: {e}")
            print(f"❌ Runtime error: {e}")
        finally:
            self.logger.info("Desktop Pet closing...")
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
    
    # Initialize logger for main entry point
    logger = get_logger("main_entry")
    logger.info("Starting Desktop Pet Application")
    logger.info(f"Pygame available: {'pygame' in sys.modules}")
    logger.info(f"Win32 available: {WIN32_AVAILABLE}")
    
    app = DesktopPetApp()
    app.run()

if __name__ == "__main__":
    main() 