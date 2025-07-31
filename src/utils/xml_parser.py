#!/usr/bin/env python3
"""
src/utils/xml_parser.py - Smart XML Parser Implementation

Handles sprite pack validation, XML parsing, and data management for desktop pets.
Supports condition-based animations and smart behavior selection.
Validates folder structure, XML files, and asset availability.
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


@dataclass
class FrameData:
    """Single animation frame data"""
    image: str
    duration: float  # in seconds
    velocity: tuple = (0, 0)  # (x, y) velocity
    sound: Optional[str] = None
    volume: Optional[int] = None


@dataclass
class AnimationBlock:
    """Smart animation block with condition support"""
    condition: Optional[str] = None  # "#{mascot.y > 100}"
    frames: List[FrameData] = field(default_factory=list)
    priority: int = 0  # For multiple conditions


@dataclass
class ActionData:
    """Smart action with multiple animation blocks"""
    name: str
    action_type: str  # Stay, Move, Animate, etc.
    animation_blocks: List[AnimationBlock] = field(default_factory=list)
    border_type: Optional[str] = None  # Floor, Wall, Ceiling
    default_animation: Optional[AnimationBlock] = None  # Fallback animation


@dataclass
class BehaviorData:
    """Smart behavior with environment awareness"""
    name: str
    frequency: int
    condition: Optional[str] = None  # "#{mascot.environment.floor.isOn(mascot.anchor)}"
    hidden: bool = False
    next_behaviors: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Validation result for a sprite pack"""
    sprite_name: str
    status: str  # READY, PARTIAL, BROKEN
    actions: Dict[str, ActionData] = field(default_factory=dict)
    behaviors: Dict[str, BehaviorData] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)


class XMLParser:
    """
    Smart XML Parser for desktop pet sprite packs.
    
    Validates sprite pack structure and parses XML configuration files.
    Supports condition-based animations and smart behavior selection.
    Stores parsed data in memory for fast runtime access.
    """
    
    def __init__(self, assets_dir: str = "assets", save2json: bool = False):
        self.assets_dir = Path(assets_dir)
        self.sprite_data: Dict[str, ValidationResult] = {}
        self.save2json = save2json
        print(f"🔍 XMLParser initialized, assets directory: {self.assets_dir}")
        if self.save2json:
            print(f"💾 JSON debug mode: ENABLED")
    
    def load_all_sprite_packs(self) -> Dict[str, str]:
        """
        Load and validate all sprite packs in assets directory.
        
        Returns:
            Dict mapping sprite_name to status (READY/PARTIAL/BROKEN)
        """
        print(f"\n🚀 Starting sprite pack discovery and validation...")
        
        if not self.assets_dir.exists():
            print(f"❌ Assets directory not found: {self.assets_dir}")
            return {}
        
        sprite_packs = {}
        folder_count = 0
        
        # Scan all folders in assets directory
        for folder_path in self.assets_dir.iterdir():
            if folder_path.is_dir():
                folder_count += 1
                sprite_name = folder_path.name
                print(f"\n📁 Validating sprite pack: {sprite_name}")
                
                # Validate and parse sprite pack
                validation_result = self._validate_sprite_pack(sprite_name)
                self.sprite_data[sprite_name] = validation_result
                sprite_packs[sprite_name] = validation_result.status
                
                # Print result
                self._print_validation_result(validation_result)
                
                # Save to JSON if enabled
                if self.save2json:
                    self._save_debug_json(validation_result)
        
        print(f"\n✅ Validation complete! Scanned {folder_count} folders, found {len(sprite_packs)} sprite packs")
        return sprite_packs
    
    def _validate_sprite_pack(self, sprite_name: str) -> ValidationResult:
        """
        Comprehensive validation of a single sprite pack.
        
        Steps:
        1. Check folder structure
        2. Check conf/ directory  
        3. Check XML files exist
        4. Validate XML syntax
        5. Check image references
        6. Check audio references
        """
        result = ValidationResult(sprite_name=sprite_name, status="BROKEN")
        sprite_path = self.assets_dir / sprite_name
        
        try:
            # Step 1: Basic folder structure
            if not self._check_folder_structure(sprite_path, result):
                return result
            
            # Step 2: Configuration directory
            conf_path = sprite_path / "conf"
            if not self._check_config_directory(conf_path, result):
                return result
            
            # Step 3: Required XML files
            actions_xml = conf_path / "actions.xml"
            behaviors_xml = conf_path / "behaviors.xml"
            if not self._check_xml_files(actions_xml, behaviors_xml, result):
                return result
            
            # Step 4: Parse XML files
            if not self._parse_xml_files(actions_xml, behaviors_xml, result):
                return result
            
            # Step 5: Validate asset references
            self._validate_asset_references(sprite_path, result)
            
            # Determine final status
            if result.errors:
                result.status = "BROKEN"
            elif result.warnings or result.missing_files:
                result.status = "PARTIAL"
            else:
                result.status = "READY"
                
        except Exception as e:
            result.errors.append(f"Unexpected error: {str(e)}")
            result.status = "BROKEN"
        
        return result
    
    def _check_folder_structure(self, sprite_path: Path, result: ValidationResult) -> bool:
        """Check basic folder structure"""
        if not sprite_path.exists():
            result.errors.append("Sprite folder not found")
            return False
        
        if not sprite_path.is_dir():
            result.errors.append("Sprite path is not a directory")
            return False
        
        # Check for any image files
        image_files = list(sprite_path.glob("*.png"))
        if not image_files:
            result.warnings.append("No PNG files found in sprite directory")
        
        return True
    
    def _check_config_directory(self, conf_path: Path, result: ValidationResult) -> bool:
        """Check conf/ directory exists"""
        if not conf_path.exists():
            result.errors.append("conf/ directory not found")
            return False
        
        if not conf_path.is_dir():
            result.errors.append("conf/ is not a directory")
            return False
        
        return True
    
    def _check_xml_files(self, actions_xml: Path, behaviors_xml: Path, result: ValidationResult) -> bool:
        """Check required XML files exist"""
        missing_files = []
        
        if not actions_xml.exists():
            missing_files.append("actions.xml")
        
        if not behaviors_xml.exists():
            missing_files.append("behaviors.xml")
        
        if missing_files:
            result.errors.append(f"Missing XML files: {', '.join(missing_files)}")
            return False
        
        return True
    
    def _parse_xml_files(self, actions_xml: Path, behaviors_xml: Path, result: ValidationResult) -> bool:
        """Parse XML files and validate syntax"""
        try:
            # Parse actions.xml
            if not self._parse_actions_xml(actions_xml, result):
                return False
            
            # Parse behaviors.xml (optional for basic functionality)
            self._parse_behaviors_xml(behaviors_xml, result)
            
            return True
            
        except Exception as e:
            result.errors.append(f"XML parsing failed: {str(e)}")
            return False
    
    def _parse_actions_xml(self, xml_path: Path, result: ValidationResult) -> bool:
        """Parse actions.xml file with support for multiple animations and conditions"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespace mapping
            namespaces = {
                'mascot': 'http://www.group-finity.com/Mascot'
            }
            
            # Find ActionList with namespace handling
            action_list = root.find('.//mascot:ActionList', namespaces)
            if action_list is None:
                # Try without namespace
                action_list = root.find('.//ActionList')
            if action_list is None:
                # Try with local-name
                action_list = root.find('.//*[local-name()="ActionList"]')
            
            if action_list is None:
                result.errors.append("ActionList not found in actions.xml")
                return False
            
            # Parse each Action with namespace handling
            actions_found = 0
            action_elements = action_list.findall('.//mascot:Action', namespaces)
            if not action_elements:
                action_elements = action_list.findall('.//Action')
            if not action_elements:
                action_elements = action_list.findall('.//*[local-name()="Action"]')
            
            for action_elem in action_elements:
                action_data = self._parse_action_element(action_elem)
                if action_data:
                    result.actions[action_data.name] = action_data
                    actions_found += 1
            
            if actions_found == 0:
                result.errors.append("No valid actions found in actions.xml")
                return False
            
            return True
            
        except ET.ParseError as e:
            result.errors.append(f"actions.xml syntax error: {str(e)}")
            return False
        except Exception as e:
            result.errors.append(f"Error parsing actions.xml: {str(e)}")
            return False
    
    def _parse_action_element(self, action_elem) -> Optional[ActionData]:
        """Parse a single Action element with support for multiple animations"""
        try:
            name = action_elem.get('Name')
            action_type = action_elem.get('Type', 'Stay')
            border_type = action_elem.get('BorderType')
            
            if not name:
                return None
            
            action = ActionData(
                name=name,
                action_type=action_type,
                border_type=border_type
            )
            
            # Parse all Animation elements (including those with conditions)
            animation_blocks = []
            default_animation = None
            
            # Define namespace mapping
            namespaces = {
                'mascot': 'http://www.group-finity.com/Mascot'
            }
            
            # Find Animation elements with namespace handling
            anim_elements = action_elem.findall('.//mascot:Animation', namespaces)
            if not anim_elements:
                anim_elements = action_elem.findall('.//Animation')
            if not anim_elements:
                anim_elements = action_elem.findall('.//*[local-name()="Animation"]')
            
            for anim_elem in anim_elements:
                animation_block = self._parse_animation_element(anim_elem)
                if animation_block:
                    if animation_block.condition:
                        # This is a conditional animation
                        animation_blocks.append(animation_block)
                    else:
                        # This is the default animation
                        default_animation = animation_block
            
            # Set the animation blocks
            action.animation_blocks = animation_blocks
            action.default_animation = default_animation
            
            # If no default animation but we have conditional ones, use the first as default
            if not default_animation and animation_blocks:
                action.default_animation = animation_blocks[0]
            
            return action
            
        except Exception as e:
            print(f"  ⚠️  Error parsing action element: {e}")
            return None
    
    def _parse_animation_element(self, anim_elem) -> Optional[AnimationBlock]:
        """Parse Animation element and create animation block"""
        try:
            # Get condition if present
            condition = anim_elem.get('Condition')
            
            animation_block = AnimationBlock(condition=condition)
            
            # Define namespace mapping
            namespaces = {
                'mascot': 'http://www.group-finity.com/Mascot'
            }
            
            # Parse Pose elements with namespace handling
            pose_elements = anim_elem.findall('.//mascot:Pose', namespaces)
            if not pose_elements:
                pose_elements = anim_elem.findall('.//Pose')
            if not pose_elements:
                pose_elements = anim_elem.findall('.//*[local-name()="Pose"]')
            
            for pose_elem in pose_elements:
                frame_data = self._parse_pose_element(pose_elem)
                if frame_data:
                    animation_block.frames.append(frame_data)
            
            return animation_block if animation_block.frames else None
                    
        except Exception as e:
            print(f"  ⚠️  Error parsing animation element: {e}")
            return None
    
    def _parse_pose_element(self, pose_elem) -> Optional[FrameData]:
        """Parse a single Pose element"""
        try:
            image = pose_elem.get('Image', '').lstrip('/')  # Remove leading slash
            duration_frames = int(pose_elem.get('Duration', 1))
            duration_seconds = duration_frames / 30.0  # Convert to seconds (30 FPS)
            
            # Parse velocity
            velocity_str = pose_elem.get('Velocity', '0,0')
            try:
                velocity = tuple(map(int, velocity_str.split(',')))
            except ValueError:
                velocity = (0, 0)
            
            # Parse sound
            sound = pose_elem.get('Sound')
            if sound:
                sound = sound.lstrip('/')  # Remove leading slash
            
            # Parse volume
            volume = pose_elem.get('Volume')
            if volume:
                try:
                    volume = int(volume)
                except ValueError:
                    volume = None
            
            return FrameData(
                image=image,
                duration=duration_seconds,
                velocity=velocity,
                sound=sound,
                volume=volume
            )
            
        except Exception as e:
            print(f"  ⚠️  Error parsing pose element: {e}")
            return None
    
    def _parse_behaviors_xml(self, xml_path: Path, result: ValidationResult):
        """Parse behaviors.xml file with support for condition wrappers"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespace mapping
            namespaces = {
                'mascot': 'http://www.group-finity.com/Mascot'
            }
            
            # Find BehaviorList with namespace handling
            behavior_list = root.find('.//mascot:BehaviorList', namespaces)
            if behavior_list is None:
                behavior_list = root.find('.//BehaviorList')
            if behavior_list is None:
                behavior_list = root.find('.//*[local-name()="BehaviorList"]')
            
            if behavior_list is None:
                result.warnings.append("BehaviorList not found in behaviors.xml")
                return
            
            # Parse behaviors including those in Condition wrappers
            self._parse_behavior_list(behavior_list, result)
                    
        except ET.ParseError as e:
            result.warnings.append(f"behaviors.xml syntax error: {str(e)}")
        except Exception as e:
            result.warnings.append(f"Error parsing behaviors.xml: {str(e)}")
    
    def _parse_behavior_list(self, behavior_list, result: ValidationResult):
        """Parse behavior list including nested condition wrappers"""
        # Define namespace mapping
        namespaces = {
            'mascot': 'http://www.group-finity.com/Mascot'
        }
        
        # Parse direct behaviors with namespace handling
        behavior_elements = behavior_list.findall('.//mascot:Behavior', namespaces)
        if not behavior_elements:
            behavior_elements = behavior_list.findall('.//Behavior')
        if not behavior_elements:
            behavior_elements = behavior_list.findall('.//*[local-name()="Behavior"]')
        
        for behavior_elem in behavior_elements:
            behavior_data = self._parse_behavior_element(behavior_elem)
            if behavior_data:
                result.behaviors[behavior_data.name] = behavior_data
        
        # Parse behaviors inside Condition wrappers
        condition_elements = behavior_list.findall('.//mascot:Condition', namespaces)
        if not condition_elements:
            condition_elements = behavior_list.findall('.//Condition')
        if not condition_elements:
            condition_elements = behavior_list.findall('.//*[local-name()="Condition"]')
        
        for condition_elem in condition_elements:
            condition_text = condition_elem.get('Condition', '')
            
            # Parse behaviors inside this condition wrapper
            inner_behavior_elements = condition_elem.findall('.//mascot:Behavior', namespaces)
            if not inner_behavior_elements:
                inner_behavior_elements = condition_elem.findall('.//Behavior')
            if not inner_behavior_elements:
                inner_behavior_elements = condition_elem.findall('.//*[local-name()="Behavior"]')
            
            for behavior_elem in inner_behavior_elements:
                behavior_data = self._parse_behavior_element(behavior_elem)
                if behavior_data:
                    # Add the wrapper condition to the behavior
                    if behavior_data.condition:
                        # Combine conditions if behavior already has one
                        behavior_data.condition = f"({condition_text}) && ({behavior_data.condition})"
                    else:
                        behavior_data.condition = condition_text
                    
                    result.behaviors[behavior_data.name] = behavior_data
    
    def _parse_behavior_element(self, behavior_elem) -> Optional[BehaviorData]:
        """Parse a single Behavior element"""
        try:
            name = behavior_elem.get('Name')
            frequency = int(behavior_elem.get('Frequency', 0))
            hidden = behavior_elem.get('Hidden', 'false').lower() == 'true'
            condition = behavior_elem.get('Condition')
            
            if not name:
                return None
            
            behavior = BehaviorData(
                name=name,
                frequency=frequency,
                hidden=hidden,
                condition=condition
            )
            
            # Parse NextBehaviorList if present
            namespaces = {
                'mascot': 'http://www.group-finity.com/Mascot'
            }
            
            next_list = behavior_elem.find('.//mascot:NextBehaviorList', namespaces)
            if next_list is None:
                next_list = behavior_elem.find('.//NextBehaviorList')
            if next_list is None:
                next_list = behavior_elem.find('.//*[local-name()="NextBehaviorList"]')
            
            if next_list is not None:
                ref_elements = next_list.findall('.//mascot:BehaviorReference', namespaces)
                if not ref_elements:
                    ref_elements = next_list.findall('.//BehaviorReference')
                if not ref_elements:
                    ref_elements = next_list.findall('.//*[local-name()="BehaviorReference"]')
                
                for ref_elem in ref_elements:
                    ref_name = ref_elem.get('Name')
                    if ref_name:
                        behavior.next_behaviors.append(ref_name)
            
            return behavior
            
        except Exception as e:
            print(f"  ⚠️  Error parsing behavior element: {e}")
            return None
    
    def _validate_asset_references(self, sprite_path: Path, result: ValidationResult):
        """Validate that all referenced assets exist"""
        # Check image references from actions
        missing_images = []
        missing_sounds = []
        
        for action in result.actions.values():
            # Check default animation
            if action.default_animation:
                for frame in action.default_animation.frames:
                    self._check_frame_assets(frame, sprite_path, missing_images, missing_sounds)
            
            # Check conditional animations
            for animation_block in action.animation_blocks:
                for frame in animation_block.frames:
                    self._check_frame_assets(frame, sprite_path, missing_images, missing_sounds)
        
        # Report missing files
        if missing_images:
            unique_missing_images = list(set(missing_images))
            if len(unique_missing_images) > 5:
                result.missing_files.extend(unique_missing_images[:5])
                result.warnings.append(f"Missing {len(unique_missing_images)} images (showing first 5)")
            else:
                result.missing_files.extend(unique_missing_images)
                result.warnings.append(f"Missing {len(unique_missing_images)} images")
        
        if missing_sounds:
            unique_missing_sounds = list(set(missing_sounds))
            result.warnings.append(f"Missing {len(unique_missing_sounds)} sound files (non-critical)")
    
    def _check_frame_assets(self, frame: FrameData, sprite_path: Path, missing_images: List[str], missing_sounds: List[str]):
        """Check if frame assets exist"""
        # Check image file
        if frame.image:
            image_path = sprite_path / frame.image
            if not image_path.exists():
                missing_images.append(frame.image)
        
        # Check sound file
        if frame.sound:
            # Try multiple possible locations
            sound_paths = [
                sprite_path / frame.sound,
                sprite_path / "sounds" / frame.sound,
                sprite_path / "audio" / frame.sound,
            ]
            
            if not any(p.exists() for p in sound_paths):
                missing_sounds.append(frame.sound)
    
    def _save_debug_json(self, result: ValidationResult):
        """Save validation result to JSON for debugging"""
        try:
            # Create debug directory
            debug_dir = Path("sprites_json_debug")
            debug_dir.mkdir(exist_ok=True)
            
            # Convert to dict for JSON serialization
            result_dict = asdict(result)
            
            # Save to file
            json_file = debug_dir / f"{result.sprite_name}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            print(f"  💾 Saved debug JSON: sprites_json_debug/{result.sprite_name}.json")
            
        except Exception as e:
            print(f"  ⚠️  Failed to save debug JSON: {e}")
    
    def _print_validation_result(self, result: ValidationResult):
        """Print validation result with nice formatting"""
        status_icon = {
            "READY": "✅",
            "PARTIAL": "⚠️ ",
            "BROKEN": "❌"
        }
        
        icon = status_icon.get(result.status, "❓")
        print(f"  {icon} Status: {result.status}")
        
        if result.actions:
            total_animations = sum(len(action.animation_blocks) for action in result.actions.values())
            print(f"  📋 Actions: {len(result.actions)} loaded ({total_animations} animation blocks)")
        
        if result.behaviors:
            conditional_behaviors = sum(1 for b in result.behaviors.values() if b.condition)
            print(f"  🎯 Behaviors: {len(result.behaviors)} loaded ({conditional_behaviors} with conditions)")
        
        if result.errors:
            for error in result.errors:
                print(f"  ❌ Error: {error}")
        
        if result.warnings:
            for warning in result.warnings[:3]:  # Show max 3 warnings
                print(f"  ⚠️  Warning: {warning}")
            if len(result.warnings) > 3:
                print(f"  ⚠️  ... and {len(result.warnings) - 3} more warnings")
        
        if result.missing_files:
            print(f"  📄 Missing files: {', '.join(result.missing_files[:3])}")
            if len(result.missing_files) > 3:
                print(f"     ... and {len(result.missing_files) - 3} more")
    
    # Public API methods for runtime access
    
    def get_actions(self, sprite_name: str) -> Dict[str, ActionData]:
        """Get parsed actions for a sprite pack"""
        if sprite_name not in self.sprite_data:
            return {}
        return self.sprite_data[sprite_name].actions
    
    def get_behaviors(self, sprite_name: str) -> Dict[str, BehaviorData]:
        """Get parsed behaviors for a sprite pack"""
        if sprite_name not in self.sprite_data:
            return {}
        return self.sprite_data[sprite_name].behaviors
    
    def get_action(self, sprite_name: str, action_name: str) -> Optional[ActionData]:
        """Get specific action data"""
        actions = self.get_actions(sprite_name)
        return actions.get(action_name)
    
    def get_animation_for_condition(self, sprite_name: str, action_name: str, sprite_state: dict) -> Optional[List[FrameData]]:
        """
        Get appropriate animation frames based on sprite state and conditions.
        
        Args:
            sprite_name: Name of the sprite pack
            action_name: Name of the action
            sprite_state: Current sprite state (position, environment, etc.)
        
        Returns:
            List of frame data for the appropriate animation, or None if not found
        """
        action = self.get_action(sprite_name, action_name)
        if not action:
            return None
        
        # Check conditional animations first
        for animation_block in action.animation_blocks:
            if animation_block.condition and self._evaluate_condition(animation_block.condition, sprite_state):
                return animation_block.frames
        
        # Fall back to default animation
        if action.default_animation:
            return action.default_animation.frames
        
        return None
    
    def _evaluate_condition(self, condition: str, sprite_state: dict) -> bool:
        """
        Evaluate a condition string against sprite state.
        
        This is a simplified evaluator. In a full implementation,
        you would want a more robust expression parser.
        """
        try:
            # Remove condition wrapper
            if condition.startswith('#{') and condition.endswith('}'):
                condition = condition[2:-1]
            elif condition.startswith('${') and condition.endswith('}'):
                condition = condition[2:-1]
            
            # Simple evaluation for common patterns
            # This is a basic implementation - you might want to use a proper expression evaluator
            
            # Example: mascot.y > 100
            if 'mascot.y' in condition:
                y = sprite_state.get('y', 0)
                if '>' in condition:
                    threshold = float(condition.split('>')[1].strip())
                    return y > threshold
                elif '<' in condition:
                    threshold = float(condition.split('<')[1].strip())
                    return y < threshold
            
            # Example: mascot.environment.floor.isOn(mascot.anchor)
            if 'mascot.environment.floor.isOn' in condition:
                return sprite_state.get('on_floor', False)
            
            # Default to True for unknown conditions (for debugging)
            return True
            
        except Exception as e:
            print(f"Warning: Could not evaluate condition '{condition}': {e}")
            return True
    
    def get_sprite_status(self, sprite_name: str) -> str:
        """Get sprite pack status (READY/PARTIAL/BROKEN)"""
        if sprite_name not in self.sprite_data:
            return "NOT_FOUND"
        return self.sprite_data[sprite_name].status
    
    def get_all_sprite_names(self) -> List[str]:
        """Get list of all loaded sprite pack names"""
        return list(self.sprite_data.keys())
    
    def get_ready_sprite_names(self) -> List[str]:
        """Get list of sprite packs ready for use"""
        return [name for name, data in self.sprite_data.items() 
                if data.status == "READY"]
    
    def print_summary(self):
        """Print summary of all loaded sprite packs"""
        print(f"\n📊 XML Parser Summary:")
        print(f"{'='*50}")
        
        total = len(self.sprite_data)
        ready = len([d for d in self.sprite_data.values() if d.status == "READY"])
        partial = len([d for d in self.sprite_data.values() if d.status == "PARTIAL"])
        broken = len([d for d in self.sprite_data.values() if d.status == "BROKEN"])
        
        print(f"Total sprite packs: {total}")
        print(f"✅ Ready: {ready}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Broken: {broken}")
        
        if ready > 0:
            print(f"\n🎮 Ready for use:")
            for name in self.get_ready_sprite_names():
                actions_count = len(self.sprite_data[name].actions)
                total_animations = sum(len(action.animation_blocks) for action in self.sprite_data[name].actions.values())
                print(f"  - {name} ({actions_count} actions, {total_animations} animation blocks)")


# Example usage and testing
if __name__ == "__main__":
    # Test the XML parser with JSON debug enabled
    parser = XMLParser(save2json=True)
    sprite_packs = parser.load_all_sprite_packs()
    parser.print_summary()
    
    # Test accessing specific data
    if sprite_packs:
        first_sprite = list(sprite_packs.keys())[0]
        print(f"\n🧪 Testing data access for '{first_sprite}':")
        
        actions = parser.get_actions(first_sprite)
        if actions:
            first_action = list(actions.values())[0]
            print(f"First action: {first_action.name} ({len(first_action.animation_blocks)} animation blocks)")
            
            if first_action.default_animation and first_action.default_animation.frames:
                first_frame = first_action.default_animation.frames[0]
                print(f"First frame: {first_frame.image} ({first_frame.duration}s)")
            
            # Test condition evaluation
            sprite_state = {'y': 150, 'on_floor': True}
            frames = parser.get_animation_for_condition(first_sprite, first_action.name, sprite_state)
            if frames:
                print(f"Condition-based animation: {len(frames)} frames")