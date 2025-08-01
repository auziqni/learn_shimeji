#!/usr/bin/env python3
"""
src/utils/json_parser.py - Smart JSON Parser Implementation

Replaces XMLParser with JSON-first approach.
Checks for JSON files, converts XML to JSON if needed.
Maintains same API and functionality as XMLParser.
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from .xml2json import XML2JSONConverter


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


class JSONParser:
    """
    Smart JSON Parser for desktop pet sprite packs.
    
    JSON-first approach: checks for JSON files, converts XML to JSON if needed.
    Maintains same API as XMLParser for seamless replacement.
    """
    
    def __init__(self, assets_dir: str = "assets", quiet_warnings: bool = True, more_data_show: bool = False):
        self.assets_dir = Path(assets_dir)
        self.sprite_data: Dict[str, ValidationResult] = {}
        self.quiet_warnings = quiet_warnings
        self.more_data_show = more_data_show
        self.xml2json_converter = XML2JSONConverter(write_existing=True, debug_mode=False)
        
        if self.more_data_show:
            print(f"🔍 JSONParser initialized, assets directory: {self.assets_dir}")
            print(f"🔇 Warning mode: {'QUIET' if quiet_warnings else 'VERBOSE'}")
    
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
                
                if self.more_data_show:
                    print(f"\n📁 Validating sprite pack: {sprite_name}")
                
                # Validate and parse sprite pack
                validation_result = self._validate_sprite_pack(sprite_name)
                self.sprite_data[sprite_name] = validation_result
                sprite_packs[sprite_name] = validation_result.status
                
                # Print result
                if self.more_data_show:
                    self._print_validation_result(validation_result)
        
        if self.more_data_show:
            print(f"\n✅ Validation complete! Scanned {folder_count} folders, found {len(sprite_packs)} sprite packs")
        return sprite_packs
    
    def _validate_sprite_pack(self, sprite_name: str) -> ValidationResult:
        """
        Comprehensive validation of a single sprite pack.
        
        Steps:
        1. Check folder structure
        2. Check conf/ directory  
        3. Check XML files exist
        4. Check JSON file exists, convert XML to JSON if needed
        5. Load from JSON
        6. Validate asset references
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
            
            # Step 4: Check JSON file, convert if needed
            json_path = conf_path / "data.json"
            if not json_path.exists():
                if self.more_data_show:
                    print(f"  🔄 JSON not found, converting XML to JSON...")
                if not self._convert_xml_to_json(sprite_path):
                    result.errors.append("Failed to convert XML to JSON")
                    return result
            
            # Step 5: Load from JSON
            if not self._load_from_json(json_path, result):
                return result
            
            # Step 6: Validate asset references
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
    
    def _convert_xml_to_json(self, sprite_path: Path) -> bool:
        """Convert XML files to JSON using xml2json converter"""
        try:
            # Use the XML2JSONConverter to convert this specific sprite pack
            conversion_result = self.xml2json_converter.convert_sprite_pack(sprite_path)
            
            if conversion_result.success:
                if self.more_data_show:
                    print(f"  ✅ Successfully converted XML to JSON")
                return True
            else:
                if self.more_data_show:
                    print(f"  ❌ Failed to convert XML to JSON: {conversion_result.validation_errors}")
                return False
                
        except Exception as e:
            if self.more_data_show:
                print(f"  ❌ Error during XML to JSON conversion: {e}")
            return False
    
    def _load_from_json(self, json_path: Path, result: ValidationResult) -> bool:
        """Load sprite data from JSON file"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Validate JSON structure
            if not self._validate_json_structure(json_data, result):
                return False
            
            # Convert JSON data to our dataclass format
            self._convert_json_to_validation_result(json_data, result)
            
            return True
            
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON format: {str(e)}")
            return False
        except Exception as e:
            result.errors.append(f"Error loading JSON: {str(e)}")
            return False
    
    def _validate_json_structure(self, json_data: dict, result: ValidationResult) -> bool:
        """Validate JSON structure has required fields"""
        required_fields = ["metadata", "actions", "behaviors", "validation"]
        
        for field in required_fields:
            if field not in json_data:
                result.errors.append(f"Missing required field in JSON: {field}")
                return False
        
        return True
    
    def _convert_json_to_validation_result(self, json_data: dict, result: ValidationResult):
        """Convert JSON data to ValidationResult format"""
        try:
            # Convert actions
            for action_name, action_data in json_data["actions"].items():
                action = self._convert_json_action(action_data)
                if action:
                    result.actions[action_name] = action
            
            # Convert behaviors
            for behavior_name, behavior_data in json_data["behaviors"].items():
                behavior = self._convert_json_behavior(behavior_data)
                if behavior:
                    result.behaviors[behavior_name] = behavior
            
            # Add validation info
            validation_info = json_data.get("validation", {})
            if not validation_info.get("success", True):
                result.errors.extend(validation_info.get("errors", []))
            result.warnings.extend(validation_info.get("warnings", []))
            
        except Exception as e:
            result.errors.append(f"Error converting JSON data: {str(e)}")
    
    def _convert_json_action(self, action_data: dict) -> Optional[ActionData]:
        """Convert JSON action data to ActionData"""
        try:
            action = ActionData(
                name=action_data["name"],
                action_type=action_data["action_type"],
                border_type=action_data.get("border_type")
            )
            
            # Convert animations
            animations = action_data.get("animations", {})
            animation_blocks = []
            
            for anim_key, anim_data in animations.items():
                animation_block = self._convert_json_animation(anim_data)
                if animation_block:
                    if anim_key == "default":
                        action.default_animation = animation_block
                    else:
                        animation_blocks.append(animation_block)
            
            action.animation_blocks = animation_blocks
            
            # If no default animation but we have conditional ones, use the first as default
            if not action.default_animation and animation_blocks:
                action.default_animation = animation_blocks[0]
            
            return action
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"  ⚠️  Error converting action: {e}")
            return None
    
    def _convert_json_animation(self, anim_data: dict) -> Optional[AnimationBlock]:
        """Convert JSON animation data to AnimationBlock"""
        try:
            animation_block = AnimationBlock(
                condition=anim_data.get("condition")
            )
            
            # Convert frames
            for frame_data in anim_data.get("frames", []):
                frame = self._convert_json_frame(frame_data)
                if frame:
                    animation_block.frames.append(frame)
            
            return animation_block if animation_block.frames else None
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"  ⚠️  Error converting animation: {e}")
            return None
    
    def _convert_json_frame(self, frame_data: dict) -> Optional[FrameData]:
        """Convert JSON frame data to FrameData"""
        try:
            return FrameData(
                image=frame_data["image"],
                duration=frame_data["duration"],
                velocity=tuple(frame_data.get("velocity", (0, 0))),
                sound=frame_data.get("sound"),
                volume=frame_data.get("volume")
            )
        except Exception as e:
            if not self.quiet_warnings:
                print(f"  ⚠️  Error converting frame: {e}")
            return None
    
    def _convert_json_behavior(self, behavior_data: dict) -> Optional[BehaviorData]:
        """Convert JSON behavior data to BehaviorData"""
        try:
            return BehaviorData(
                name=behavior_data["name"],
                frequency=behavior_data["frequency"],
                condition=behavior_data.get("condition"),
                hidden=behavior_data.get("hidden", False),
                next_behaviors=behavior_data.get("next_behaviors", [])
            )
        except Exception as e:
            if not self.quiet_warnings:
                print(f"  ⚠️  Error converting behavior: {e}")
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
    
    # Public API methods - same as XMLParser
    
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
        print(f"\n📊 JSON Parser Summary:")
        print(f"{'='*50}")
        
        total = len(self.sprite_data)
        ready = len([d for d in self.sprite_data.values() if d.status == "READY"])
        partial = len([d for d in self.sprite_data.values() if d.status == "PARTIAL"])
        broken = len([d for d in self.sprite_data.values() if d.status == "BROKEN"])
        
        print(f"Total sprite packs: {total}")
        print(f"✅ Ready: {ready}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Broken: {broken}")
        
        if ready > 0 and self.more_data_show:
            print(f"\n🎮 Ready for use:")
            for name in self.get_ready_sprite_names():
                actions_count = len(self.sprite_data[name].actions)
                total_animations = sum(len(action.animation_blocks) for action in self.sprite_data[name].actions.values())
                print(f"  - {name} ({actions_count} actions, {total_animations} animation blocks)")


# Example usage and testing
if __name__ == "__main__":
    # Test the JSON parser
    parser = JSONParser(more_data_show=True)
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