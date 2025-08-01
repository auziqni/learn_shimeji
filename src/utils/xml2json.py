#!/usr/bin/env python3
"""
src/utils/xml2json.py - XML to JSON Converter

Converts actions.xml and behaviors.xml to clean JSON structure.
Preserves all data while adding type categorization for behaviors.
Outputs JSON files for sprite packs with validation.
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict


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
    """Animation block with condition support"""
    condition: Optional[str] = None
    frames: List[FrameData] = field(default_factory=list)
    priority: int = 0


@dataclass
class ActionData:
    """Action data with animations"""
    name: str
    action_type: str
    border_type: Optional[str] = None
    draggable: Optional[bool] = None
    loop: Optional[bool] = None
    animations: Dict[str, AnimationBlock] = field(default_factory=dict)
    action_references: List[Dict[str, Any]] = field(default_factory=list)  # For Sequence actions
    embedded_data: Dict[str, Any] = field(default_factory=dict)  # For Embedded actions


@dataclass
class BehaviorData:
    """Behavior data with categorization"""
    name: str
    frequency: int
    hidden: bool = False
    condition: Optional[str] = None
    next_behaviors: List[str] = field(default_factory=list)
    action: Optional[str] = None
    type: str = "unknown"  # system, ai, interaction, transition


@dataclass
class ConversionResult:
    """Result of XML to JSON conversion"""
    sprite_name: str
    actions: Dict[str, ActionData] = field(default_factory=dict)
    behaviors: Dict[str, BehaviorData] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    success: bool = False


class XML2JSONConverter:
    """
    Converts XML files to JSON structure.
    Preserves all data while adding type categorization.
    """
    
    def __init__(self, write_existing: bool = False, debug_mode: bool = False):
        """
        Initialize converter
        
        Args:
            write_existing: Whether to write JSON for existing sprite packs
            debug_mode: Enable debug output and detailed logging
        """
        self.write_existing = write_existing
        self.debug_mode = debug_mode
        
        if self.debug_mode:
            print(f"🔧 XML2JSON Converter initialized")
            print(f"  Write existing: {self.write_existing}")
            print(f"  Debug mode: {self.debug_mode}")
    
    def convert_sprite_pack(self, sprite_path: Path) -> ConversionResult:
        """
        Convert a single sprite pack from XML to JSON
        
        Args:
            sprite_path: Path to sprite pack directory
            
        Returns:
            ConversionResult with converted data and validation info
        """
        sprite_name = sprite_path.name
        result = ConversionResult(sprite_name=sprite_name)
        
        try:
            # Check if sprite pack exists
            if not sprite_path.exists():
                result.validation_errors.append(f"Sprite pack directory not found: {sprite_path}")
                return result
            
            # Check conf directory
            conf_path = sprite_path / "conf"
            if not conf_path.exists():
                result.validation_errors.append(f"conf/ directory not found in {sprite_name}")
                return result
            
            # Check XML files
            actions_xml = conf_path / "actions.xml"
            behaviors_xml = conf_path / "behaviors.xml"
            
            if not actions_xml.exists():
                result.validation_errors.append(f"actions.xml not found in {sprite_name}")
                return result
            
            if not behaviors_xml.exists():
                result.validation_errors.append(f"behaviors.xml not found in {sprite_name}")
                return result
            
            # Parse actions.xml
            if self.debug_mode:
                print(f"  📋 Parsing actions.xml for {sprite_name}")
            
            actions_result = self._parse_actions_xml(actions_xml, sprite_path)
            result.actions = actions_result["actions"]
            result.warnings.extend(actions_result["warnings"])
            
            # Parse behaviors.xml
            if self.debug_mode:
                print(f"  🧠 Parsing behaviors.xml for {sprite_name}")
            
            behaviors_result = self._parse_behaviors_xml(behaviors_xml)
            result.behaviors = behaviors_result["behaviors"]
            result.warnings.extend(behaviors_result["warnings"])
            
            # Categorize behaviors
            self._categorize_behaviors(result.behaviors)
            
            # Validate next_behavior references
            validation_errors = self._validate_next_behaviors(result.behaviors)
            result.validation_errors.extend(validation_errors)
            
            # Determine success
            result.success = len(result.validation_errors) == 0
            
            if self.debug_mode:
                print(f"  ✅ Conversion complete for {sprite_name}")
                print(f"    Actions: {len(result.actions)}")
                print(f"    Behaviors: {len(result.behaviors)}")
                print(f"    Errors: {len(result.validation_errors)}")
                print(f"    Warnings: {len(result.warnings)}")
            
            return result
            
        except Exception as e:
            result.validation_errors.append(f"Unexpected error: {str(e)}")
            result.success = False
            return result
    
    def _parse_actions_xml(self, xml_path: Path, sprite_path: Path) -> Dict[str, Any]:
        """Parse actions.xml file"""
        result = {"actions": {}, "warnings": []}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespace
            namespace = {'mascot': 'http://www.group-finity.com/Mascot'}
            
            # Find all ActionList elements
            action_lists = root.findall('.//mascot:ActionList', namespace)
            if not action_lists:
                # Try without namespace
                action_lists = root.findall('.//ActionList')
            
            if not action_lists:
                result["warnings"].append("ActionList not found in actions.xml")
                return result
            
            # Parse each ActionList
            for action_list in action_lists:
                for action_elem in action_list.findall('.//mascot:Action', namespace):
                    action_data = self._parse_action_element(action_elem, sprite_path, namespace)
                    if action_data:
                        result["actions"][action_data.name] = action_data
            
            if self.debug_mode:
                print(f"    Parsed {len(result['actions'])} actions")
            
            return result
            
        except Exception as e:
            result["warnings"].append(f"Error parsing actions.xml: {str(e)}")
            return result
    
    def _parse_action_element(self, action_elem, sprite_path: Path, namespace: dict = None) -> Optional[ActionData]:
        """Parse a single Action element"""
        try:
            name = action_elem.get('Name')
            action_type = action_elem.get('Type', 'Stay')
            border_type = action_elem.get('BorderType')
            draggable = action_elem.get('Draggable')
            loop = action_elem.get('Loop')
            
            if not name:
                return None
            
            action = ActionData(
                name=name,
                action_type=action_type,
                border_type=border_type,
                draggable=draggable.lower() == 'true' if draggable else None,
                loop=loop.lower() == 'true' if loop else None
            )
            
            # Parse Embedded actions (Java-specific but we'll include them)
            if action_type == "Embedded":
                if self.debug_mode:
                    print(f"    Including {name} (Type: {action_type})")
                # Parse Embedded action with class information
                embedded_data = {
                    "class": action_elem.get('Class'),
                    "offset_x": action_elem.get('OffsetX'),
                    "offset_y": action_elem.get('OffsetY'),
                    "born_x": action_elem.get('BornX'),
                    "born_y": action_elem.get('BornY'),
                    "born_behavior": action_elem.get('BornBehavior')
                }
                # Remove None values
                embedded_data = {k: v for k, v in embedded_data.items() if v is not None}
                
                action.embedded_data = embedded_data
            
            # Parse animations for Stay/Move/Animate actions
            if action_type in ["Stay", "Move", "Animate"]:
                animations = {}
                for anim_elem in action_elem.findall('.//mascot:Animation', namespace):
                    animation_block = self._parse_animation_element(anim_elem, namespace)
                    if animation_block:
                        if animation_block.condition:
                            animations[f"conditional_{len(animations)}"] = animation_block
                        else:
                            animations["default"] = animation_block
                
                action.animations = animations
            
            # Parse ActionReference for Sequence actions
            elif action_type == "Sequence":
                action_references = []
                for ref_elem in action_elem.findall('.//mascot:ActionReference', namespace):
                    ref_data = self._parse_action_reference_element(ref_elem, namespace)
                    if ref_data:
                        action_references.append(ref_data)
                
                # Store action references as a special field
                action.action_references = action_references
            
            return action
            
        except Exception as e:
            if self.debug_mode:
                print(f"    Warning: Error parsing action {name}: {e}")
            return None
    
    def _parse_action_reference_element(self, ref_elem, namespace: dict = None) -> Optional[Dict[str, Any]]:
        """Parse ActionReference element"""
        try:
            ref_name = ref_elem.get('Name')
            duration = ref_elem.get('Duration')
            target_x = ref_elem.get('TargetX')
            target_y = ref_elem.get('TargetY')
            initial_vx = ref_elem.get('InitialVX')
            initial_vy = ref_elem.get('InitialVY')
            look_right = ref_elem.get('LookRight')
            x_offset = ref_elem.get('X')
            y_offset = ref_elem.get('Y')
            
            if not ref_name:
                return None
            
            ref_data = {
                "name": ref_name,
                "duration": duration,
                "target_x": target_x,
                "target_y": target_y,
                "initial_vx": initial_vx,
                "initial_vy": initial_vy,
                "look_right": look_right,
                "x_offset": x_offset,
                "y_offset": y_offset
            }
            
            # Remove None values
            ref_data = {k: v for k, v in ref_data.items() if v is not None}
            
            return ref_data
            
        except Exception as e:
            if self.debug_mode:
                print(f"    Warning: Error parsing action reference: {e}")
            return None
    
    def _parse_animation_element(self, anim_elem, namespace=None) -> Optional[AnimationBlock]:
        """Parse Animation element"""
        try:
            condition = anim_elem.get('Condition')
            animation_block = AnimationBlock(condition=condition)
            
            # Parse Pose elements
            for pose_elem in anim_elem.findall('.//mascot:Pose', namespace):
                frame_data = self._parse_pose_element(pose_elem)
                if frame_data:
                    animation_block.frames.append(frame_data)
            
            return animation_block if animation_block.frames else None
            
        except Exception as e:
            if self.debug_mode:
                print(f"    Warning: Error parsing animation: {e}")
            return None
    
    def _parse_pose_element(self, pose_elem) -> Optional[FrameData]:
        """Parse a single Pose element"""
        try:
            image = pose_elem.get('Image', '').lstrip('/')
            duration_frames = int(pose_elem.get('Duration', 1))
            duration_seconds = duration_frames / 30.0  # Convert to seconds
            
            # Parse velocity
            velocity_str = pose_elem.get('Velocity', '0,0')
            try:
                velocity = tuple(map(int, velocity_str.split(',')))
            except ValueError:
                velocity = (0, 0)
            
            # Parse sound
            sound = pose_elem.get('Sound')
            if sound:
                sound = sound.lstrip('/')
            
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
            if self.debug_mode:
                print(f"    Warning: Error parsing pose: {e}")
            return None
    
    def _parse_behaviors_xml(self, xml_path: Path) -> Dict[str, Any]:
        """Parse behaviors.xml file"""
        result = {"behaviors": {}, "warnings": []}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespace
            namespace = {'mascot': 'http://www.group-finity.com/Mascot'}
            
            # Find BehaviorList
            behavior_list = root.find('.//mascot:BehaviorList', namespace)
            if behavior_list is None:
                # Try without namespace
                behavior_list = root.find('.//BehaviorList')
            
            if behavior_list is None:
                result["warnings"].append("BehaviorList not found in behaviors.xml")
                return result
            
            # Parse direct behaviors
            for behavior_elem in behavior_list.findall('.//mascot:Behavior', namespace):
                behavior_data = self._parse_behavior_element(behavior_elem, namespace)
                if behavior_data:
                    result["behaviors"][behavior_data.name] = behavior_data
            
            # Parse behaviors inside Condition wrappers
            for condition_elem in behavior_list.findall('.//mascot:Condition', namespace):
                condition_text = condition_elem.get('Condition', '')
                
                for behavior_elem in condition_elem.findall('.//mascot:Behavior', namespace):
                    behavior_data = self._parse_behavior_element(behavior_elem, namespace)
                    if behavior_data:
                        # Add wrapper condition
                        if behavior_data.condition:
                            behavior_data.condition = f"({condition_text}) && ({behavior_data.condition})"
                        else:
                            behavior_data.condition = condition_text
                        
                        result["behaviors"][behavior_data.name] = behavior_data
            
            if self.debug_mode:
                print(f"    Parsed {len(result['behaviors'])} behaviors")
            
            return result
            
        except Exception as e:
            result["warnings"].append(f"Error parsing behaviors.xml: {str(e)}")
            return result
    
    def _parse_behavior_element(self, behavior_elem, namespace: dict = None) -> Optional[BehaviorData]:
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
            
            # Parse NextBehaviorList
            next_list = behavior_elem.find('.//mascot:NextBehaviorList', namespace)
            if next_list is not None:
                for ref_elem in next_list.findall('.//mascot:BehaviorReference', namespace):
                    ref_name = ref_elem.get('Name')
                    if ref_name:
                        behavior.next_behaviors.append(ref_name)
            
            return behavior
            
        except Exception as e:
            if self.debug_mode:
                print(f"    Warning: Error parsing behavior {name}: {e}")
            return None
    
    def _categorize_behaviors(self, behaviors: Dict[str, BehaviorData]):
        """Categorize behaviors by type"""
        for behavior_data in behaviors.values():
            behavior_data.type = self._determine_behavior_type(behavior_data)
    
    def _determine_behavior_type(self, behavior: BehaviorData) -> str:
        """Determine behavior type based on name, frequency, and hidden status"""
        name = behavior.name
        frequency = behavior.frequency
        hidden = behavior.hidden
        
        # System behaviors (ALWAYS REQUIRED)
        system_behaviors = ["ChaseMouse", "Fall", "Dragged", "Thrown", "Divided"]
        if name in system_behaviors:
            return "system"
        
        # AI behaviors (Frequency > 0, user-visible)
        if frequency > 0 and not hidden:
            return "ai"
        
        # Interaction behaviors (Pet-related)
        interaction_keywords = ["Pet", "BePet"]
        if any(keyword in name for keyword in interaction_keywords):
            return "interaction"
        
        # Transition behaviors (Internal transitions)
        transition_keywords = ["After", "Short", "Continue", "Stop"]
        if any(keyword in name for keyword in transition_keywords):
            return "transition"
        
        # Default categorization
        if frequency == 0 and hidden:
            return "transition"  # Default for hidden behaviors
        else:
            return "ai"  # Default for visible behaviors
    
    def _validate_next_behaviors(self, behaviors: Dict[str, BehaviorData]) -> List[str]:
        """Validate next_behavior references"""
        errors = []
        valid_behaviors = set(behaviors.keys())
        
        for behavior_name, behavior_data in behaviors.items():
            for next_behavior in behavior_data.next_behaviors:
                if next_behavior not in valid_behaviors:
                    errors.append(
                        f"Behavior '{behavior_name}' references non-existent behavior '{next_behavior}'"
                    )
        
        return errors
    
    def convert_all_sprite_packs(self, assets_dir: str = "assets") -> Dict[str, ConversionResult]:
        """
        Convert all sprite packs in assets directory
        
        Args:
            assets_dir: Path to assets directory
            
        Returns:
            Dict mapping sprite_name to ConversionResult
        """
        assets_path = Path(assets_dir)
        results = {}
        
        if not assets_path.exists():
            print(f"❌ Assets directory not found: {assets_path}")
            return results
        
        sprite_packs = [d for d in assets_path.iterdir() if d.is_dir()]
        
        if self.debug_mode:
            print(f"🚀 Converting {len(sprite_packs)} sprite packs...")
        
        for sprite_path in sprite_packs:
            sprite_name = sprite_path.name
            
            # Check if JSON already exists
            json_path = sprite_path / "conf" / "data.json"
            if json_path.exists() and not self.write_existing:
                if self.debug_mode:
                    print(f"  ⏭️  Skipping {sprite_name} (JSON already exists)")
                continue
            
            if self.debug_mode:
                print(f"  🔄 Converting {sprite_name}...")
            
            result = self.convert_sprite_pack(sprite_path)
            results[sprite_name] = result
            
            # Write JSON file if conversion successful
            if result.success:
                self._write_json_file(result, sprite_path)
            else:
                if self.debug_mode:
                    print(f"  ❌ Conversion failed for {sprite_name}")
        
        return results
    
    def _write_json_file(self, result: ConversionResult, sprite_path: Path):
        """Write conversion result to JSON file"""
        try:
            conf_path = sprite_path / "conf"
            json_path = conf_path / "data.json"
            
            # Prepare JSON data
            json_data = {
                "metadata": {
                    "sprite_name": result.sprite_name,
                    "conversion_date": "2024-01-01",
                    "original_files": ["actions.xml", "behaviors.xml"]
                },
                "actions": {name: asdict(action) for name, action in result.actions.items()},
                "behaviors": {name: asdict(behavior) for name, behavior in result.behaviors.items()},
                "validation": {
                    "success": result.success,
                    "errors": result.validation_errors,
                    "warnings": result.warnings
                }
            }
            
            # Write to file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            if self.debug_mode:
                print(f"  💾 Wrote {json_path}")
                
        except Exception as e:
            if self.debug_mode:
                print(f"  ⚠️  Failed to write JSON: {e}")


# Example usage
if __name__ == "__main__":
    # Test conversion
    converter = XML2JSONConverter(write_existing=True, debug_mode=True)
    results = converter.convert_all_sprite_packs()
    
    # Print summary
    print(f"\n📊 Conversion Summary:")
    successful = sum(1 for r in results.values() if r.success)
    total = len(results)
    print(f"  Total sprite packs: {total}")
    print(f"  Successful conversions: {successful}")
    print(f"  Failed conversions: {total - successful}")
    
    for sprite_name, result in results.items():
        status = "✅" if result.success else "❌"
        print(f"  {status} {sprite_name}: {len(result.actions)} actions, {len(result.behaviors)} behaviors") 