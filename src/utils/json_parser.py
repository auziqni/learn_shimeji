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
        
        # Find all sprite pack directories
        sprite_dirs = [d for d in self.assets_dir.iterdir() 
                      if d.is_dir() and not d.name.startswith('.')]
        
        if not sprite_dirs:
            print(f"❌ No sprite packs found in {self.assets_dir}")
            return {}
        
        print(f"📁 Found {len(sprite_dirs)} sprite pack(s):")
        for sprite_dir in sprite_dirs:
            print(f"  - {sprite_dir.name}")
        
        # Validate each sprite pack
        results = {}
        for sprite_dir in sprite_dirs:
            sprite_name = sprite_dir.name
            result = self._validate_sprite_pack(sprite_name)
            self.sprite_data[sprite_name] = result
            results[sprite_name] = result.status
            
            if self.more_data_show:
                self._print_validation_result(result)
        
        return results
    
    def _validate_sprite_pack(self, sprite_name: str) -> ValidationResult:
        """
        Validate a single sprite pack and load its data.
        
        Args:
            sprite_name: Name of the sprite pack
            
        Returns:
            ValidationResult with status and data
        """
        result = ValidationResult(sprite_name=sprite_name, status="BROKEN")
        sprite_path = self.assets_dir / sprite_name
        
        if not sprite_path.exists():
            result.errors.append(f"Sprite pack directory not found: {sprite_path}")
            return result
        
        # Check folder structure
        if not self._check_folder_structure(sprite_path, result):
            return result
        
        # Check config directory
        conf_path = sprite_path / "conf"
        if not self._check_config_directory(conf_path, result):
            return result
        
        # Check for XML files
        actions_xml = conf_path / "actions.xml"
        behaviors_xml = conf_path / "behaviors.xml"
        
        if not self._check_xml_files(actions_xml, behaviors_xml, result):
            return result
        
        # Try to convert XML to JSON if needed
        json_path = conf_path / "data.json"
        if not json_path.exists():
            if not self._convert_xml_to_json(sprite_path):
                result.errors.append("Failed to convert XML to JSON")
                return result
        
        # Load from JSON
        if not self._load_from_json(json_path, result):
            return result
        
        # Validate asset references
        self._validate_asset_references(sprite_path, result)
        
        # Determine final status
        if not result.errors:
            result.status = "READY"
        elif len(result.errors) <= 2:
            result.status = "PARTIAL"
        else:
            result.status = "BROKEN"
        
        return result
    
    def _check_folder_structure(self, sprite_path: Path, result: ValidationResult) -> bool:
        """Check basic folder structure"""
        required_dirs = ["conf", "sounds"]
        
        for req_dir in required_dirs:
            dir_path = sprite_path / req_dir
            if not dir_path.exists():
                result.errors.append(f"Missing required directory: {req_dir}")
                return False
        
        return True
    
    def _check_config_directory(self, conf_path: Path, result: ValidationResult) -> bool:
        """Check config directory contents"""
        if not conf_path.exists():
            result.errors.append("Config directory not found")
            return False
        
        return True
    
    def _check_xml_files(self, actions_xml: Path, behaviors_xml: Path, result: ValidationResult) -> bool:
        """Check if XML files exist"""
        if not actions_xml.exists():
            result.errors.append("actions.xml not found")
            return False
        
        if not behaviors_xml.exists():
            result.errors.append("behaviors.xml not found")
            return False
        
        return True
    
    def _convert_xml_to_json(self, sprite_path: Path) -> bool:
        """Convert XML files to JSON using XML2JSONConverter"""
        try:
            result = self.xml2json_converter.convert_sprite_pack(sprite_path)
            return result.success
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to convert XML to JSON for {sprite_path.name}: {e}")
            return False
    
    def _load_from_json(self, json_path: Path, result: ValidationResult) -> bool:
        """Load and parse JSON data"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not self._validate_json_structure(json_data, result):
                return False
            
            self._convert_json_to_validation_result(json_data, result)
            return True
            
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON format: {e}")
            return False
        except Exception as e:
            result.errors.append(f"Failed to load JSON: {e}")
            return False
    
    def _validate_json_structure(self, json_data: dict, result: ValidationResult) -> bool:
        """Validate JSON structure"""
        required_keys = ["actions", "behaviors"]
        
        for key in required_keys:
            if key not in json_data:
                result.errors.append(f"Missing required key: {key}")
                return False
        
        return True
    
    def _convert_json_to_validation_result(self, json_data: dict, result: ValidationResult):
        """Convert JSON data to ValidationResult"""
        # Convert actions
        for action_name, action_data in json_data.get("actions", {}).items():
            action = self._convert_json_action(action_data)
            if action:
                result.actions[action_name] = action
        
        # Convert behaviors
        for behavior_name, behavior_data in json_data.get("behaviors", {}).items():
            behavior = self._convert_json_behavior(behavior_data)
            if behavior:
                result.behaviors[behavior_name] = behavior
    
    def _convert_json_action(self, action_data: dict) -> Optional[ActionData]:
        """Convert JSON action data to ActionData"""
        try:
            name = action_data.get("name", "")
            action_type = action_data.get("action_type", "")
            
            action = ActionData(name=name, action_type=action_type)
            
            # Convert animations
            animations = action_data.get("animations", {})
            for anim_name, anim_data in animations.items():
                animation = self._convert_json_animation(anim_data)
                if animation:
                    action.animation_blocks.append(animation)
            
            # Set default animation if available
            if action.animation_blocks:
                action.default_animation = action.animation_blocks[0]
            
            return action
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to convert action: {e}")
            return None
    
    def _convert_json_animation(self, anim_data: dict) -> Optional[AnimationBlock]:
        """Convert JSON animation data to AnimationBlock"""
        try:
            animation = AnimationBlock()
            
            # Set condition if present
            if "condition" in anim_data:
                animation.condition = anim_data["condition"]
            
            # Convert frames
            frames = anim_data.get("frames", [])
            for frame_data in frames:
                frame = self._convert_json_frame(frame_data)
                if frame:
                    animation.frames.append(frame)
            
            return animation
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to convert animation: {e}")
            return None
    
    def _convert_json_frame(self, frame_data: dict) -> Optional[FrameData]:
        """Convert JSON frame data to FrameData"""
        try:
            image = frame_data.get("image", "")
            duration = frame_data.get("duration", 0.1)
            velocity = frame_data.get("velocity", (0, 0))
            sound = frame_data.get("sound")
            volume = frame_data.get("volume")
            
            return FrameData(
                image=image,
                duration=duration,
                velocity=velocity,
                sound=sound,
                volume=volume
            )
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to convert frame: {e}")
            return None
    
    def _convert_json_behavior(self, behavior_data: dict) -> Optional[BehaviorData]:
        """Convert JSON behavior data to BehaviorData"""
        try:
            name = behavior_data.get("name", "")
            frequency = behavior_data.get("frequency", 1)
            condition = behavior_data.get("condition")
            hidden = behavior_data.get("hidden", False)
            next_behaviors = behavior_data.get("next_behaviors", [])
            
            return BehaviorData(
                name=name,
                frequency=frequency,
                condition=condition,
                hidden=hidden,
                next_behaviors=next_behaviors
            )
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to convert behavior: {e}")
            return None
    
    def _validate_asset_references(self, sprite_path: Path, result: ValidationResult):
        """Validate that referenced assets exist"""
        missing_images = []
        missing_sounds = []
        
        # Check action assets
        for action in result.actions.values():
            for animation in action.animation_blocks:
                for frame in animation.frames:
                    self._check_frame_assets(frame, sprite_path, missing_images, missing_sounds)
        
        # Add missing files to result
        if missing_images:
            result.missing_files.extend(missing_images)
            result.warnings.append(f"Missing {len(missing_images)} image files")
        
        if missing_sounds:
            result.missing_files.extend(missing_sounds)
            result.warnings.append(f"Missing {len(missing_sounds)} sound files")
    
    def _check_frame_assets(self, frame: FrameData, sprite_path: Path, missing_images: List[str], missing_sounds: List[str]):
        """Check if frame assets exist"""
        # Check image
        if frame.image:
            image_path = sprite_path / frame.image
            if not image_path.exists():
                missing_images.append(str(image_path))
        
        # Check sound
        if frame.sound:
            sound_path = sprite_path / "sounds" / frame.sound
            if not sound_path.exists():
                missing_sounds.append(str(sound_path))
    
    def _print_validation_result(self, result: ValidationResult):
        """Print detailed validation result"""
        status_emoji = {
            "READY": "✅",
            "PARTIAL": "⚠️",
            "BROKEN": "❌"
        }
        
        print(f"\n{status_emoji.get(result.status, '❓')} {result.sprite_name}: {result.status}")
        
        if result.actions:
            print(f"  📋 Actions: {len(result.actions)}")
            for action_name in result.actions.keys():
                print(f"    - {action_name}")
        
        if result.behaviors:
            print(f"  🧠 Behaviors: {len(result.behaviors)}")
            for behavior_name in result.behaviors.keys():
                print(f"    - {behavior_name}")
        
        if result.errors:
            print(f"  ❌ Errors: {len(result.errors)}")
            for error in result.errors:
                print(f"    - {error}")
        
        if result.warnings:
            print(f"  ⚠️ Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"    - {warning}")
    
    def get_actions(self, sprite_name: str) -> Dict[str, ActionData]:
        """Get all actions for a sprite"""
        if sprite_name in self.sprite_data:
            return self.sprite_data[sprite_name].actions
        return {}
    
    def get_actions_by_type(self, sprite_name: str, action_type: str) -> Dict[str, ActionData]:
        """Get actions filtered by action type"""
        all_actions = self.get_actions(sprite_name)
        filtered_actions = {}
        
        for action_name, action_data in all_actions.items():
            if action_data.action_type == action_type:
                filtered_actions[action_name] = action_data
        
        return filtered_actions
    
    def get_behaviors(self, sprite_name: str) -> Dict[str, BehaviorData]:
        """Get all behaviors for a sprite"""
        if sprite_name in self.sprite_data:
            return self.sprite_data[sprite_name].behaviors
        return {}
    
    def get_action(self, sprite_name: str, action_name: str) -> Optional[ActionData]:
        """Get specific action for a sprite"""
        actions = self.get_actions(sprite_name)
        return actions.get(action_name)
    
    def get_animation_for_condition(self, sprite_name: str, action_name: str, sprite_state: dict) -> Optional[List[FrameData]]:
        """
        Get animation frames for a specific condition.
        
        Args:
            sprite_name: Name of the sprite
            action_name: Name of the action
            sprite_state: Current sprite state (position, environment, etc.)
            
        Returns:
            List of FrameData or None if no matching animation
        """
        action = self.get_action(sprite_name, action_name)
        if not action:
            return None
        
        # Find animation block that matches condition
        matching_animation = None
        highest_priority = -1
        
        for animation in action.animation_blocks:
            if animation.condition:
                if self._evaluate_condition(animation.condition, sprite_state):
                    if animation.priority > highest_priority:
                        matching_animation = animation
                        highest_priority = animation.priority
            else:
                # Default animation (no condition)
                if not matching_animation:
                    matching_animation = animation
        
        return matching_animation.frames if matching_animation else None
    
    def _evaluate_condition(self, condition: str, sprite_state: dict) -> bool:
        """
        Evaluate a condition string against sprite state.
        
        Args:
            condition: Condition string like "#{mascot.y > 100}"
            sprite_state: Current sprite state
            
        Returns:
            True if condition is met
        """
        try:
            # Simple condition evaluation
            # This is a basic implementation - can be extended for more complex conditions
            
            # Remove #{ and } from condition
            clean_condition = condition.strip()
            if clean_condition.startswith("#{") and clean_condition.endswith("}"):
                clean_condition = clean_condition[2:-1]
            
            # Replace mascot references with sprite_state values
            # This is a simplified version - real implementation would be more sophisticated
            eval_condition = clean_condition
            
            # Basic variable substitution
            for key, value in sprite_state.items():
                eval_condition = eval_condition.replace(f"mascot.{key}", str(value))
            
            # Safe evaluation (basic arithmetic and comparisons only)
            # In production, use a proper expression parser
            return eval(eval_condition, {"__builtins__": {}}, {})
            
        except Exception as e:
            if not self.quiet_warnings:
                print(f"⚠️ Failed to evaluate condition '{condition}': {e}")
            return False
    
    def get_sprite_status(self, sprite_name: str) -> str:
        """Get status of a sprite pack"""
        if sprite_name in self.sprite_data:
            return self.sprite_data[sprite_name].status
        return "UNKNOWN"
    
    def get_all_sprite_names(self) -> List[str]:
        """Get all sprite names"""
        return list(self.sprite_data.keys())
    
    def get_ready_sprite_names(self) -> List[str]:
        """Get names of ready sprite packs"""
        return [name for name, data in self.sprite_data.items() 
                if data.status == "READY"]
    
    def print_summary(self):
        """Print summary of all sprite packs"""
        if not self.sprite_data:
            print("No sprite data loaded. Call load_all_sprite_packs() first.")
            return
        
        ready_count = len([d for d in self.sprite_data.values() if d.status == "READY"])
        partial_count = len([d for d in self.sprite_data.values() if d.status == "PARTIAL"])
        broken_count = len([d for d in self.sprite_data.values() if d.status == "BROKEN"])
        
        print(f"\n📊 Sprite Pack Summary:")
        print(f"  ✅ Ready: {ready_count}")
        print(f"  ⚠️ Partial: {partial_count}")
        print(f"  ❌ Broken: {broken_count}")
        print(f"  📁 Total: {len(self.sprite_data)}") 