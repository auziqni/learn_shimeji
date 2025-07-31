#!/usr/bin/env python3
"""
test/test_animation_system.py - Animation System Tester

Interactive testing tool untuk sistem animasi dengan:
- Sprite pack selection
- XML parsing validation
- Animation testing dengan visual interface
- Performance testing untuk 25+ pets
"""

import pygame
import sys
import os
import time
from typing import Dict, Any, Optional, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import our existing modules
    from src.animation import Animation, clear_global_sprite_cache, get_global_sprite_cache_size, clear_global_sound_cache, get_global_sound_cache_size
    from src.utils.xml_parser import XMLParser
    
    ANIMATION_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Error importing modules: {e}")
    ANIMATION_SYSTEM_AVAILABLE = False


class AnimationSystemTester:
    """Interactive animation system tester"""
    
    def __init__(self):
        try:
            # Initialize Pygame
            pygame.init()
            
            # Initialize mixer for sound
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("✅ Sound system initialized")
            except Exception as e:
                print(f"⚠️  Sound system not available: {e}")
            
            self.screen = pygame.display.set_mode((1000, 700))
            pygame.display.set_caption("Animation System Tester")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
            
            # Test variables
            self.current_sprite_pack = None
            self.available_sprite_packs = self._discover_sprite_packs()
            self.current_animation = None
            self.available_actions = []
            self.current_action_index = 0
            self.xml_parser = XMLParser()
            
            # Performance testing
            self.test_animations = []
            self.performance_mode = False
            
            print("Animation System Tester initialized")
            print(f"Available sprite packs: {self.available_sprite_packs}")
            
        except Exception as e:
            print(f"Error initializing tester: {e}")
            raise
    
    def _discover_sprite_packs(self) -> List[str]:
        """Discover available sprite packs in assets directory"""
        sprite_packs = []
        assets_dir = "assets"
        
        if os.path.exists(assets_dir):
            for item in os.listdir(assets_dir):
                item_path = os.path.join(assets_dir, item)
                if os.path.isdir(item_path):
                    # Check if it has conf directory with XML files
                    conf_path = os.path.join(item_path, "conf")
                    if os.path.exists(conf_path):
                        actions_xml = os.path.join(conf_path, "actions.xml")
                        if os.path.exists(actions_xml):
                            sprite_packs.append(item)
        
        return sprite_packs
    
    def test_xml_parsing(self, sprite_pack: str) -> Dict[str, Any]:
        """Test XML parsing untuk sprite pack"""
        print(f"\n=== Testing XML Parsing for {sprite_pack} ===")
        
        try:
            # Load all sprite packs first
            self.xml_parser.load_all_sprite_packs()
            
            # Get actions for specific sprite pack
            actions = self.xml_parser.get_actions(sprite_pack)
            behaviors = self.xml_parser.get_behaviors(sprite_pack)
            
            if actions:
                print(f"✅ Successfully parsed XML files")
                print(f"📋 Found {len(actions)} actions:")
                for action_name in sorted(actions.keys()):
                    action_data = actions[action_name]
                    anim_count = len(action_data.animation_blocks) if action_data.animation_blocks else 0
                    print(f"   - {action_name} ({action_data.action_type}) - {anim_count} animation blocks")
                
                if behaviors:
                    print(f"🎯 Found {len(behaviors)} behaviors:")
                    for behavior_name in sorted(behaviors.keys()):
                        behavior_data = behaviors[behavior_name]
                        hidden_str = " (hidden)" if behavior_data.hidden else ""
                        print(f"   - {behavior_name} (freq: {behavior_data.frequency}){hidden_str}")
                
                return {
                    'success': True,
                    'actions': len(actions),
                    'behaviors': len(behaviors) if behaviors else 0,
                    'action_names': list(actions.keys())
                }
            else:
                print("❌ No actions found in XML")
                return {'success': False, 'error': 'No actions found'}
                
        except Exception as e:
            print(f"❌ Error during XML parsing: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_animation_creation(self, sprite_pack: str) -> bool:
        """Test animation creation dari XML data"""
        print(f"\n=== Testing Animation Creation for {sprite_pack} ===")
        
        try:
            actions = self.xml_parser.get_actions(sprite_pack)
            if not actions:
                print("❌ No actions available")
                return False
            
            # Test creating animations from XML data
            created_animations = {}
            for action_name, action_data in actions.items():
                if action_data.default_animation and action_data.default_animation.frames:
                    # Convert ActionData to frame format
                    frames_data = []
                    for frame in action_data.default_animation.frames:
                        frame_data = {
                            'Image': frame.image,
                            'ImageAnchor': '64,128',
                            'Velocity': f"{frame.velocity[0]},{frame.velocity[1]}",
                            'Duration': str(int(frame.duration * 30))  # Convert to frame units
                        }
                        
                        # Add sound data if available
                        if frame.sound:
                            frame_data['Sound'] = frame.sound
                        if frame.volume is not None:
                            frame_data['Volume'] = frame.volume
                        
                        frames_data.append(frame_data)
                    
                    # Create animation with correct sprite pack path
                    sprite_pack_path = f"assets/{sprite_pack}"
                    animation = Animation(sprite_pack_path, action_name, frames_data)
                    created_animations[action_name] = animation
                    
                    # Debug: Verify animation is using correct sprite pack
                    if action_name == list(actions.keys())[0]:  # First animation
                        print(f"   Debug: Animation '{action_name}' created with path: {sprite_pack_path}")
                        # Check if sprite is actually loaded
                        if animation.get_frame_count() > 0:
                            first_frame = animation.get_current_frame()
                            if first_frame and first_frame.image:
                                print(f"   Debug: First frame sprite size: {first_frame.image.get_size()}")
                                print(f"   Debug: Sprite cache size after loading: {get_global_sprite_cache_size()}")
                                
                                # Check sound data
                                if first_frame.sound:
                                    print(f"   Debug: First frame has sound: {first_frame.sound}")
                                    if first_frame.volume is not None:
                                        print(f"   Debug: Sound volume: {first_frame.volume}")
                                else:
                                    print(f"   Debug: First frame has no sound")
                            else:
                                print(f"   Debug: No sprite loaded for first frame")
                        else:
                            print(f"   Debug: Animation has no frames")
            
            if created_animations:
                self.available_actions = list(created_animations.keys())
                print(f"✅ Created {len(created_animations)} animations successfully")
                for action_name in sorted(created_animations.keys()):
                    anim = created_animations[action_name]
                    print(f"   - {action_name}: {anim.get_frame_count()} frames")
                
                # Store animations for testing
                self.test_animations = list(created_animations.values())
                return True
            else:
                print("❌ No animations could be created")
                return False
                
        except Exception as e:
            print(f"❌ Error creating animations: {e}")
            return False
    
    def test_sprite_loading(self, sprite_pack: str) -> Dict[str, Any]:
        """Test sprite loading dari XML references"""
        print(f"\n=== Testing Sprite Loading for {sprite_pack} ===")
        
        try:
            actions = self.xml_parser.get_actions(sprite_pack)
            sprite_references = set()
            sound_references = set()
            
            # Collect all sprite and sound references from XML
            for action_name, action_data in actions.items():
                if action_data.default_animation:
                    for frame in action_data.default_animation.frames:
                        sprite_references.add(frame.image)
                        if frame.sound:
                            sound_references.add(frame.sound)
            
            # Test loading sprites
            loaded_sprites = 0
            missing_sprites = []
            
            for sprite_ref in sprite_references:
                sprite_path = os.path.join(f"assets/{sprite_pack}", sprite_ref)
                if os.path.exists(sprite_path):
                    loaded_sprites += 1
                else:
                    missing_sprites.append(sprite_ref)
            
            # Test loading sounds
            loaded_sounds = 0
            missing_sounds = []
            
            for sound_ref in sound_references:
                sound_path = os.path.join(f"assets/{sprite_pack}/sounds", sound_ref)
                if os.path.exists(sound_path):
                    loaded_sounds += 1
                else:
                    missing_sounds.append(sound_ref)
            
            print(f"📁 Total sprite references: {len(sprite_references)}")
            print(f"✅ Successfully found: {loaded_sprites}")
            print(f"❌ Missing sprites: {len(missing_sprites)}")
            
            print(f"🔊 Total sound references: {len(sound_references)}")
            print(f"✅ Successfully found: {loaded_sounds}")
            print(f"❌ Missing sounds: {len(missing_sounds)}")
            
            if missing_sprites:
                print("Missing sprite files:")
                for sprite in missing_sprites[:10]:  # Show first 10
                    print(f"   - {sprite}")
                if len(missing_sprites) > 10:
                    print(f"   ... and {len(missing_sprites) - 10} more")
            
            if missing_sounds:
                print("Missing sound files:")
                for sound in missing_sounds[:10]:  # Show first 10
                    print(f"   - {sound}")
                if len(missing_sounds) > 10:
                    print(f"   ... and {len(missing_sounds) - 10} more")
            
            return {
                'total_sprites': len(sprite_references),
                'loaded_sprites': loaded_sprites,
                'missing_sprites': missing_sprites,
                'total_sounds': len(sound_references),
                'loaded_sounds': loaded_sounds,
                'missing_sounds': missing_sounds
            }
            
        except Exception as e:
            print(f"❌ Error testing sprite loading: {e}")
            return {
                'total_sprites': 0,
                'loaded_sprites': 0,
                'missing_sprites': [],
                'total_sounds': 0,
                'loaded_sounds': 0,
                'missing_sounds': [],
                'error': str(e)
            }
    
    def run_interactive_test(self, sprite_pack: str):
        """Run interactive animation test"""
        print(f"\n=== Interactive Animation Test for {sprite_pack} ===")
        print("Controls:")
        print("  LEFT/RIGHT arrows: Switch animations")
        print("  A: Previous sprite pack")
        print("  S: Next sprite pack")
        print("  SPACE: Restart current animation")
        print("  P: Toggle performance mode (25+ animations)")
        print("  M: Toggle sound (mute/unmute)")
        print("  ESC: Exit")
        print("  F1: Print current animation info")
        
        if not self.test_animations:
            print("❌ No animations available")
            return
        
        try:
            # Start dengan animation pertama
            self.current_action_index = 0
            self.current_animation = self.test_animations[0]
            self.current_animation.play()
            
            running = True
            while running:
                dt = self.clock.tick(30) / 1000.0  # 30 FPS
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_LEFT:
                            self._previous_animation()
                        elif event.key == pygame.K_RIGHT:
                            self._next_animation()
                        elif event.key == pygame.K_a:
                            self._previous_sprite_pack()
                        elif event.key == pygame.K_s:
                            self._next_sprite_pack()
                        elif event.key == pygame.K_SPACE:
                            self._restart_animation()
                        elif event.key == pygame.K_p:
                            self._toggle_performance_mode()
                        elif event.key == pygame.K_m:
                            self._toggle_sound()
                        elif event.key == pygame.K_F1:
                            self._print_animation_info()
                
                # Update animations
                if self.performance_mode:
                    # Update all animations for performance testing
                    for anim in self.test_animations:
                        anim.update(dt)
                else:
                    # Update only current animation
                    if self.current_animation:
                        self.current_animation.update(dt)
                
                # Draw
                self._draw_test_screen()
                
        except Exception as e:
            print(f"Error during interactive test: {e}")
    
    def _next_animation(self):
        """Switch ke animasi berikutnya"""
        try:
            if self.test_animations:
                self.current_action_index = (self.current_action_index + 1) % len(self.test_animations)
                self.current_animation = self.test_animations[self.current_action_index]
                self.current_animation.play()
                print(f"Switched to: {self.current_animation.get_animation_name()}")
        except Exception as e:
            print(f"Error switching animation: {e}")
    
    def _previous_animation(self):
        """Switch ke animasi sebelumnya"""
        try:
            if self.test_animations:
                self.current_action_index = (self.current_action_index - 1) % len(self.test_animations)
                self.current_animation = self.test_animations[self.current_action_index]
                self.current_animation.play()
                print(f"Switched to: {self.current_animation.get_animation_name()}")
        except Exception as e:
            print(f"Error switching animation: {e}")
    
    def _restart_animation(self):
        """Restart animasi saat ini"""
        try:
            if self.current_animation:
                self.current_animation.play()
                print(f"Restarted: {self.current_animation.get_animation_name()}")
        except Exception as e:
            print(f"Error restarting animation: {e}")
    
    def _toggle_performance_mode(self):
        """Toggle performance testing mode"""
        self.performance_mode = not self.performance_mode
        mode = "ON" if self.performance_mode else "OFF"
        print(f"Performance mode: {mode} ({len(self.test_animations)} animations)")
    
    def _toggle_sound(self):
        """Toggle sound for all animations"""
        if self.test_animations:
            # Toggle sound for first animation (they all share the same setting)
            sound_enabled = not self.test_animations[0].get_sound_enabled()
            for anim in self.test_animations:
                anim.set_sound_enabled(sound_enabled)
            
            status = "ON" if sound_enabled else "OFF"
            print(f"Sound: {status}")
        else:
            print("No animations available for sound control")
    
    def _next_sprite_pack(self):
        """Switch ke sprite pack berikutnya"""
        try:
            if len(self.available_sprite_packs) > 1:
                current_index = self.available_sprite_packs.index(self.current_sprite_pack)
                next_index = (current_index + 1) % len(self.available_sprite_packs)
                new_sprite_pack = self.available_sprite_packs[next_index]
                self._switch_sprite_pack(new_sprite_pack)
        except Exception as e:
            print(f"Error switching sprite pack: {e}")
    
    def _previous_sprite_pack(self):
        """Switch ke sprite pack sebelumnya"""
        try:
            if len(self.available_sprite_packs) > 1:
                current_index = self.available_sprite_packs.index(self.current_sprite_pack)
                prev_index = (current_index - 1) % len(self.available_sprite_packs)
                new_sprite_pack = self.available_sprite_packs[prev_index]
                self._switch_sprite_pack(new_sprite_pack)
        except Exception as e:
            print(f"Error switching sprite pack: {e}")
    
    def _switch_sprite_pack(self, new_sprite_pack: str):
        """Switch ke sprite pack baru"""
        try:
            print(f"\n🔄 Switching to sprite pack: {new_sprite_pack}")
            
            # Clear current animations and reset state
            self.test_animations.clear()
            self.current_animation = None
            self.current_action_index = 0
            self.available_actions = []
            
            # Clear global sprite and sound cache to force reload of new assets
            old_sprite_cache_size = get_global_sprite_cache_size()
            old_sound_cache_size = get_global_sound_cache_size()
            clear_global_sprite_cache()
            clear_global_sound_cache()
            print(f"   Cleared sprite cache (was {old_sprite_cache_size} sprites)")
            print(f"   Cleared sound cache (was {old_sound_cache_size} sounds)")
            
            # Update current sprite pack
            self.current_sprite_pack = new_sprite_pack
            
            # Force reload XML data for new sprite pack
            self.xml_parser.load_all_sprite_packs()
            
            # Reload animations for new sprite pack
            animation_created = self.test_animation_creation(new_sprite_pack)
            
            if animation_created and self.test_animations:
                self.current_animation = self.test_animations[0]
                self.current_animation.play()
                new_sprite_cache_size = get_global_sprite_cache_size()
                new_sound_cache_size = get_global_sound_cache_size()
                print(f"✅ Switched to {new_sprite_pack} with {len(self.test_animations)} animations")
                print(f"   First animation: {self.current_animation.get_animation_name()}")
                print(f"   New sprite cache size: {new_sprite_cache_size} sprites")
                print(f"   New sound cache size: {new_sound_cache_size} sounds")
                
                # Verify sprites are actually loaded
                if self.current_animation.get_frame_count() > 0:
                    first_frame = self.current_animation.get_current_frame()
                    if first_frame and first_frame.image:
                        print(f"   ✅ Sprite loaded successfully: {first_frame.image.get_size()}")
                        # Check if this is actually a different sprite
                        sprite_hash = hash(first_frame.image.get_buffer().raw)
                        print(f"   Debug: Sprite hash: {sprite_hash}")
                    else:
                        print(f"   ❌ No sprite loaded for current frame")
                else:
                    print(f"   ❌ No frames in current animation")
            else:
                print(f"❌ Failed to load animations for {new_sprite_pack}")
                
        except Exception as e:
            print(f"Error switching sprite pack: {e}")
    
    def _print_animation_info(self):
        """Print informasi animasi saat ini"""
        try:
            if self.current_animation:
                print(f"\n=== Current Animation Info ===")
                print(f"Name: {self.current_animation.get_animation_name()}")
                print(f"Frame Count: {self.current_animation.get_frame_count()}")
                print(f"Current Frame: {self.current_animation.get_current_frame_index()}")
                print(f"Is Playing: {self.current_animation.is_playing}")
                print(f"Is Looping: {self.current_animation.is_looping}")
                
                current_frame = self.current_animation.get_current_frame()
                if current_frame:
                    print(f"Frame Size: {current_frame.image.get_size()}")
                    print(f"Frame Anchor: {current_frame.image_anchor}")
                    print(f"Frame Velocity: {current_frame.velocity}")
                print("==============================\n")
        except Exception as e:
            print(f"Error getting animation info: {e}")
    
    def _draw_test_screen(self):
        """Draw test screen"""
        try:
            # Clear screen
            self.screen.fill((50, 50, 50))
            
            # Draw sprites
            if self.performance_mode:
                # Draw all animations in performance mode
                for i, anim in enumerate(self.test_animations):
                    current_frame = anim.get_current_frame()
                    if current_frame:
                        sprite = current_frame.image
                        sprite_rect = sprite.get_rect()
                        # Arrange in grid
                        row = i // 5
                        col = i % 5
                        sprite_rect.x = 50 + col * 180
                        sprite_rect.y = 50 + row * 150
                        self.screen.blit(sprite, sprite_rect)
                        
                        # Draw label
                        label = self.small_font.render(anim.get_animation_name(), True, (255, 255, 255))
                        self.screen.blit(label, (sprite_rect.x, sprite_rect.y + sprite_rect.height + 5))
            else:
                # Draw single animation
                if self.current_animation:
                    current_frame = self.current_animation.get_current_frame()
                    if current_frame:
                        sprite = current_frame.image
                        sprite_rect = sprite.get_rect()
                        sprite_rect.center = (500, 300)
                        self.screen.blit(sprite, sprite_rect)
            
            # Draw UI info
            y_offset = 10
            ui_texts = [
                f"Sprite Pack: {self.current_sprite_pack or 'None'} ({self.available_sprite_packs.index(self.current_sprite_pack) + 1}/{len(self.available_sprite_packs)})",
                f"Performance Mode: {'ON' if self.performance_mode else 'OFF'}",
                f"Sound: {'ON' if self.test_animations and self.test_animations[0].get_sound_enabled() else 'OFF'}",
                f"Animations: {len(self.test_animations)}",
            ]
            
            if not self.performance_mode and self.current_animation:
                ui_texts.extend([
                    f"Current: {self.current_animation.get_animation_name()}",
                    f"Frame: {self.current_animation.get_current_frame_index() + 1}/{self.current_animation.get_frame_count()}",
                ])
            
            ui_texts.extend([
                f"Controls: LEFT/RIGHT arrows, A/S sprite packs, SPACE, P, M, F1, ESC",
            ])
            
            for text in ui_texts:
                text_surface = self.font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25
            
            # Draw available animations list
            if not self.performance_mode:
                y_offset = 500
                list_title = self.font.render("Available Animations:", True, (200, 200, 255))
                self.screen.blit(list_title, (10, y_offset))
                y_offset += 25
                
                for i, anim in enumerate(self.test_animations):
                    color = (255, 255, 0) if i == self.current_action_index else (180, 180, 180)
                    anim_text = self.small_font.render(f"{i+1}. {anim.get_animation_name()}", True, color)
                    self.screen.blit(anim_text, (10, y_offset))
                    y_offset += 18
            
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error drawing screen: {e}")
    
    def run_full_test_suite(self, sprite_pack: str):
        """Run full test suite"""
        print(f"\n{'='*60}")
        print(f"🧪 FULL ANIMATION SYSTEM TEST SUITE")
        print(f"📦 Sprite Pack: {sprite_pack}")
        print(f"{'='*60}")
        
        self.current_sprite_pack = sprite_pack
        
        # Test 1: XML Parsing
        xml_results = self.test_xml_parsing(sprite_pack)
        
        # Test 2: Animation Creation
        animation_created = self.test_animation_creation(sprite_pack)
        
        # Test 3: Sprite Loading
        sprite_results = self.test_sprite_loading(sprite_pack)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"XML Parsing: {'✅ PASS' if xml_results.get('success') else '❌ FAIL'}")
        print(f"Animation Creation: {'✅ PASS' if animation_created else '❌ FAIL'}")
        print(f"Sprite Loading: {sprite_results['loaded_sprites']}/{sprite_results['total_sprites']} loaded")
        print(f"Sound Loading: {sprite_results['loaded_sounds']}/{sprite_results['total_sounds']} loaded")
        print(f"Animation System: {'✅ AVAILABLE' if ANIMATION_SYSTEM_AVAILABLE else '❌ NOT AVAILABLE'}")
        
        overall_success = (xml_results.get('success', False) and 
                          animation_created and 
                          sprite_results['loaded_sprites'] > 0)
        
        print(f"Overall Status: {'✅ READY FOR USE' if overall_success else '❌ NEEDS ATTENTION'}")
        
        return {
            'xml_parsing': xml_results.get('success', False),
            'animation_creation': animation_created,
            'sprites_loaded': sprite_results['loaded_sprites'],
            'total_sprites': sprite_results['total_sprites'],
            'sounds_loaded': sprite_results['loaded_sounds'],
            'total_sounds': sprite_results['total_sounds'],
            'animation_system_available': ANIMATION_SYSTEM_AVAILABLE,
            'overall_success': overall_success
        }


def main():
    """Main function"""
    try:
        # Create tester
        tester = AnimationSystemTester()
        
        if not tester.available_sprite_packs:
            print("❌ No sprite packs found in assets/ directory")
            print("Please add sprite packs to assets/")
            return 1
        
        # Select sprite pack
        if len(sys.argv) > 1:
            sprite_pack = sys.argv[1]
            if sprite_pack not in tester.available_sprite_packs:
                print(f"❌ Sprite pack '{sprite_pack}' not found")
                print(f"Available: {tester.available_sprite_packs}")
                return 1
        else:
            # Show available sprite packs
            print("Available sprite packs:")
            for i, pack in enumerate(tester.available_sprite_packs):
                print(f"  {i+1}. {pack}")
            
            # Use first available
            sprite_pack = tester.available_sprite_packs[0]
            print(f"🎯 Testing with: {sprite_pack}")
        
        # Run tests
        results = tester.run_full_test_suite(sprite_pack)
        
        # Start interactive test directly if successful
        if results['overall_success']:
            print(f"\n🎮 Starting interactive test...")
            try:
                tester.run_interactive_test(sprite_pack)
            except KeyboardInterrupt:
                print("\nTest interrupted by user")
        else:
            print(f"\n❌ Cannot start interactive test - system not ready")
        
        # Cleanup
        clear_global_sprite_cache()
        pygame.quit()
        
        # Return exit code
        return 0 if results['overall_success'] else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 