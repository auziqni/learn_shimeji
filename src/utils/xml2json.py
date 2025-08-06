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
    image_anchor: Optional[tuple] = None  # (x, y) anchor point
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
            ConversionResult with success status and data
        """
        result = ConversionResult(sprite_name=sprite_path.name)
        
        if self.debug_mode:
            print(f"🔄 Converting sprite pack: {sprite_path.name}")
        
        # Check if sprite pack exists
        if not sprite_path.exists():
            result.validation_errors.append(f"Sprite pack directory not found: {sprite_path}")
            return result
        
        # Check for required files
        conf_path = sprite_path / "conf"
        actions_xml = conf_path / "actions.xml"
        behaviors_xml = conf_path / "behaviors.xml"
        
        if not actions_xml.exists():
            result.validation_errors.append("actions.xml not found")
            return result
        
        if not behaviors_xml.exists():
            result.validation_errors.append("behaviors.xml not found")
            return result
        
        # Parse actions.xml
        try:
            actions_data = self._parse_actions_xml(actions_xml, sprite_path)
            result.actions = actions_data
        except Exception as e:
            result.validation_errors.append(f"Failed to parse actions.xml: {e}")
            if self.debug_mode:
                print(f"❌ Error parsing actions.xml: {e}")
        
        # Parse behaviors.xml
        try:
            behaviors_data = self._parse_behaviors_xml(behaviors_xml)
            result.behaviors = behaviors_data
        except Exception as e:
            result.validation_errors.append(f"Failed to parse behaviors.xml: {e}")
            if self.debug_mode:
                print(f"❌ Error parsing behaviors.xml: {e}")
        
        # Categorize behaviors
        self._categorize_behaviors(result.behaviors)
        
        # Validate next behaviors
        warnings = self._validate_next_behaviors(result.behaviors)
        result.warnings.extend(warnings)
        
        # Determine success
        result.success = len(result.validation_errors) == 0
        
        if self.debug_mode:
            print(f"✅ Conversion {'successful' if result.success else 'failed'}")
            print(f"  Actions: {len(result.actions)}")
            print(f"  Behaviors: {len(result.behaviors)}")
            print(f"  Errors: {len(result.validation_errors)}")
            print(f"  Warnings: {len(result.warnings)}")
        
        return result
    
    def _parse_actions_xml(self, xml_path: Path, sprite_path: Path) -> Dict[str, ActionData]:
        """
        Parse actions.xml file
        
        Args:
            xml_path: Path to actions.xml
            sprite_path: Path to sprite pack directory
            
        Returns:
            Dict mapping action names to ActionData
        """
        actions = {}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Handle namespaces - the XML uses default namespace
            # Extract namespace from root element
            if '}' in root.tag:
                namespace_uri = root.tag.split('}')[0].strip('{')
                namespace = {'ns': namespace_uri}
            else:
                # No namespace found, use empty dict
                namespace = {}
            
            if self.debug_mode:
                print(f"🔍 Parsing XML with namespace: {namespace}")
            
            # Find all Action elements - try both with and without namespace
            action_elements = []
            
            # Try with namespace first
            if namespace:
                action_elements = root.findall('.//ns:Action', namespace)
                if self.debug_mode:
                    print(f"🔍 Found {len(action_elements)} actions with namespace")
            
            # If no actions found with namespace, try without namespace
            if not action_elements:
                action_elements = root.findall('.//Action')
                if self.debug_mode:
                    print(f"🔍 Found {len(action_elements)} actions without namespace")
            
            # If still no actions, try with default namespace handling
            if not action_elements:
                # Register the namespace with ElementTree
                ET.register_namespace('', namespace.get('ns', ''))
                action_elements = root.findall('.//Action')
                if self.debug_mode:
                    print(f"🔍 Found {len(action_elements)} actions with registered namespace")
            
            for action_elem in action_elements:
                action = self._parse_action_element(action_elem, sprite_path, namespace)
                if action:
                    actions[action.name] = action
            
            if self.debug_mode:
                print(f"📋 Parsed {len(actions)} actions from {xml_path.name}")
            
        except ET.ParseError as e:
            if self.debug_mode:
                print(f"❌ XML parse error in {xml_path.name}: {e}")
            raise
        
        return actions
    
    def _parse_action_element(self, action_elem, sprite_path: Path, namespace: dict = None) -> Optional[ActionData]:
        """
        Parse a single action element
        
        Args:
            action_elem: XML element for action
            sprite_path: Path to sprite pack
            namespace: XML namespace dict
            
        Returns:
            ActionData or None if parsing failed
        """
        try:
            # Get basic action info - XML uses capitalized attributes
            name = action_elem.get('Name', '')
            action_type = action_elem.get('Type', '')
            
            # Skip actions without name
            if not name:
                if self.debug_mode:
                    print(f"⚠️ Skipping action without name: Type={action_type}")
                return None
            
            action = ActionData(name=name, action_type=action_type)
            
            # Get optional attributes - check both capitalized and lowercase
            border_type = action_elem.get('BorderType') or action_elem.get('border')
            if border_type:
                action.border_type = border_type
            
            draggable = action_elem.get('Draggable') or action_elem.get('draggable')
            if draggable:
                action.draggable = draggable == 'true'
            
            loop = action_elem.get('Loop') or action_elem.get('loop')
            if loop:
                action.loop = loop == 'true'
            
            # Parse animations - try both with and without namespace
            anim_elements = []
            
            # Try with namespace first
            if namespace:
                anim_elements = action_elem.findall('.//ns:Animation', namespace)
            
            # If no animations found with namespace, try without namespace
            if not anim_elements:
                anim_elements = action_elem.findall('.//Animation')
            
            for anim_elem in anim_elements:
                animation = self._parse_animation_element(anim_elem, namespace)
                if animation:
                    # Use condition as key, or default
                    anim_key = animation.condition or "default"
                    action.animations[anim_key] = animation
            
            # Parse action references (for Sequence actions) - try both with and without namespace
            ref_elements = []
            if namespace:
                ref_elements = action_elem.findall('.//ns:ActionReference', namespace)
            if not ref_elements:
                ref_elements = action_elem.findall('.//ActionReference')
            
            for ref_elem in ref_elements:
                ref_data = self._parse_action_reference_element(ref_elem, namespace)
                if ref_data:
                    action.action_references.append(ref_data)
            
            # Parse embedded data - try both with and without namespace
            embed_elements = []
            if namespace:
                embed_elements = action_elem.findall('.//ns:Embedded', namespace)
            if not embed_elements:
                embed_elements = action_elem.findall('.//Embedded')
            
            for embed_elem in embed_elements:
                embed_key = embed_elem.get('name', '')
                embed_value = embed_elem.text or ''
                if embed_key:
                    action.embedded_data[embed_key] = embed_value
            
            return action
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Failed to parse action element: {e}")
            return None
    
    def _parse_action_reference_element(self, ref_elem, namespace: dict = None) -> Optional[Dict[str, Any]]:
        """
        Parse action reference element
        
        Args:
            ref_elem: XML element for action reference
            namespace: XML namespace dict
            
        Returns:
            Dict with reference data or None
        """
        try:
            ref_data = {
                'name': ref_elem.get('name', ''),
                'type': ref_elem.get('type', ''),
                'parameters': {}
            }
            
            # Parse parameters
            for param_elem in ref_elem.findall('.//ns:parameter', namespace or {}):
                param_name = param_elem.get('name', '')
                param_value = param_elem.text or ''
                if param_name:
                    ref_data['parameters'][param_name] = param_value
            
            return ref_data
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Failed to parse action reference: {e}")
            return None
    
    def _parse_animation_element(self, anim_elem, namespace=None) -> Optional[AnimationBlock]:
        """
        Parse animation element
        
        Args:
            anim_elem: XML element for animation
            namespace: XML namespace dict
            
        Returns:
            AnimationBlock or None
        """
        try:
            animation = AnimationBlock()
            
            # Get condition
            condition = anim_elem.get('condition')
            if condition:
                animation.condition = condition
            
            # Get priority
            priority = anim_elem.get('priority')
            if priority:
                try:
                    animation.priority = int(priority)
                except ValueError:
                    animation.priority = 0
            
            # Parse frames/poses - try both with and without namespace
            pose_elements = []
            
            # Try with namespace first
            if namespace:
                pose_elements = anim_elem.findall('.//ns:Pose', namespace)
            
            # If no poses found with namespace, try without namespace
            if not pose_elements:
                pose_elements = anim_elem.findall('.//Pose')
            
            for pose_elem in pose_elements:
                frame = self._parse_pose_element(pose_elem)
                if frame:
                    animation.frames.append(frame)
            
            return animation
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Failed to parse animation: {e}")
            return None
    
    def _parse_pose_element(self, pose_elem) -> Optional[FrameData]:
        """
        Parse pose element (animation frame)
        
        Args:
            pose_elem: XML element for pose/frame
            
        Returns:
            FrameData or None (None if ImageAnchor is missing/invalid)
        """
        try:
            # Get attributes - check both capitalized and lowercase
            image = pose_elem.get('Image') or pose_elem.get('image', '')
            duration = pose_elem.get('Duration') or pose_elem.get('duration', '0.1')
            velocity = pose_elem.get('Velocity') or pose_elem.get('velocity', '0,0')
            sound = pose_elem.get('Sound') or pose_elem.get('sound')
            volume = pose_elem.get('Volume') or pose_elem.get('volume')
            
            # Parse ImageAnchor - skip frame if missing or invalid
            image_anchor_str = pose_elem.get('ImageAnchor')
            if not image_anchor_str:
                if self.debug_mode:
                    print(f"⚠️ Skipping frame {image}: ImageAnchor missing")
                return None
            
            try:
                # Parse "64,128" format to (64, 128)
                anchor_parts = image_anchor_str.split(',')
                if len(anchor_parts) != 2:
                    if self.debug_mode:
                        print(f"⚠️ Skipping frame {image}: Invalid ImageAnchor format '{image_anchor_str}'")
                    return None
                
                anchor_x = float(anchor_parts[0].strip())
                anchor_y = float(anchor_parts[1].strip())
                image_anchor = (anchor_x, anchor_y)
                
            except (ValueError, IndexError) as e:
                if self.debug_mode:
                    print(f"⚠️ Skipping frame {image}: Invalid ImageAnchor '{image_anchor_str}' - {e}")
                return None
            
            # Parse velocity from "x,y" format
            try:
                vel_parts = velocity.split(',')
                if len(vel_parts) == 2:
                    vel_x = float(vel_parts[0].strip())
                    vel_y = float(vel_parts[1].strip())
                else:
                    vel_x = vel_y = 0.0
            except (ValueError, IndexError):
                vel_x = vel_y = 0.0
            
            # Convert to proper types
            try:
                duration_val = float(duration)
            except ValueError:
                duration_val = 0.1
            
            try:
                volume_val = int(volume) if volume else None
            except ValueError:
                volume_val = None
            
            return FrameData(
                image=image,
                duration=duration_val,
                velocity=(vel_x, vel_y),
                image_anchor=image_anchor,
                sound=sound,
                volume=volume_val
            )
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Failed to parse pose: {e}")
            return None
    
    def _parse_behaviors_xml(self, xml_path: Path) -> Dict[str, BehaviorData]:
        """
        Parse behaviors.xml file
        
        Args:
            xml_path: Path to behaviors.xml
            
        Returns:
            Dict mapping behavior names to BehaviorData
        """
        behaviors = {}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Handle namespaces - the XML uses default namespace
            if '}' in root.tag:
                namespace_uri = root.tag.split('}')[0].strip('{')
                namespace = {'ns': namespace_uri}
            else:
                # No namespace found, use empty dict
                namespace = {}
            
            if self.debug_mode:
                print(f"🔍 Parsing behaviors XML with namespace: {namespace}")
            
            # Find all Behavior elements - try both with and without namespace
            behavior_elements = []
            
            # Try with namespace first
            if namespace:
                behavior_elements = root.findall('.//ns:Behavior', namespace)
                if self.debug_mode:
                    print(f"🔍 Found {len(behavior_elements)} behaviors with namespace")
            
            # If no behaviors found with namespace, try without namespace
            if not behavior_elements:
                behavior_elements = root.findall('.//Behavior')
                if self.debug_mode:
                    print(f"🔍 Found {len(behavior_elements)} behaviors without namespace")
            
            # If still no behaviors, try with default namespace handling
            if not behavior_elements:
                # Register the namespace with ElementTree
                ET.register_namespace('', namespace.get('ns', ''))
                behavior_elements = root.findall('.//Behavior')
                if self.debug_mode:
                    print(f"🔍 Found {len(behavior_elements)} behaviors with registered namespace")
            
            for behavior_elem in behavior_elements:
                behavior = self._parse_behavior_element(behavior_elem, namespace)
                if behavior:
                    behaviors[behavior.name] = behavior
            
            if self.debug_mode:
                print(f"🧠 Parsed {len(behaviors)} behaviors from {xml_path.name}")
            
        except ET.ParseError as e:
            if self.debug_mode:
                print(f"❌ XML parse error in {xml_path.name}: {e}")
            raise
        
        return behaviors
    
    def _parse_behavior_element(self, behavior_elem, namespace: dict = None) -> Optional[BehaviorData]:
        """
        Parse a single behavior element
        
        Args:
            behavior_elem: XML element for behavior
            namespace: XML namespace dict
            
        Returns:
            BehaviorData or None
        """
        try:
            # Get attributes - check both capitalized and lowercase
            name = behavior_elem.get('Name') or behavior_elem.get('name', '')
            frequency = behavior_elem.get('Frequency') or behavior_elem.get('frequency', '1')
            hidden = behavior_elem.get('Hidden') or behavior_elem.get('hidden', 'false')
            condition = behavior_elem.get('Condition') or behavior_elem.get('condition')
            action = behavior_elem.get('Action') or behavior_elem.get('action')
            
            # Skip behaviors without name
            if not name:
                if self.debug_mode:
                    print(f"⚠️ Skipping behavior without name: Frequency={frequency}")
                return None
            
            # Parse next behaviors - try both with and without namespace
            next_behaviors = []
            
            # Try to find NextBehaviorList elements
            next_list_elements = []
            if namespace:
                next_list_elements = behavior_elem.findall('.//ns:NextBehaviorList', namespace)
            if not next_list_elements:
                next_list_elements = behavior_elem.findall('.//NextBehaviorList')
            
            for next_list_elem in next_list_elements:
                # Try to find BehaviorReference elements
                ref_elements = []
                if namespace:
                    ref_elements = next_list_elem.findall('.//ns:BehaviorReference', namespace)
                if not ref_elements:
                    ref_elements = next_list_elem.findall('.//BehaviorReference')
                
                for ref_elem in ref_elements:
                    ref_name = ref_elem.get('Name') or ref_elem.get('name', '')
                    if ref_name:
                        next_behaviors.append(ref_name)
            
            # Convert to proper types
            try:
                frequency_val = int(frequency)
            except ValueError:
                frequency_val = 1
            
            hidden_val = hidden.lower() == 'true'
            
            return BehaviorData(
                name=name,
                frequency=frequency_val,
                hidden=hidden_val,
                condition=condition,
                action=action,
                next_behaviors=next_behaviors
            )
            
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Failed to parse behavior: {e}")
            return None
    
    def _categorize_behaviors(self, behaviors: Dict[str, BehaviorData]):
        """
        Categorize behaviors by type
        
        Args:
            behaviors: Dict of behaviors to categorize
        """
        for behavior in behaviors.values():
            behavior.type = self._determine_behavior_type(behavior)
    
    def _determine_behavior_type(self, behavior: BehaviorData) -> str:
        """
        Determine the type of a behavior
        
        Args:
            behavior: Behavior to categorize
            
        Returns:
            Behavior type string
        """
        name_lower = behavior.name.lower()
        
        # System behaviors
        system_keywords = ['start', 'stop', 'init', 'shutdown', 'reset']
        if any(keyword in name_lower for keyword in system_keywords):
            return "system"
        
        # AI behaviors
        ai_keywords = ['think', 'decide', 'plan', 'choose', 'random']
        if any(keyword in name_lower for keyword in ai_keywords):
            return "ai"
        
        # Interaction behaviors
        interaction_keywords = ['click', 'drag', 'hover', 'select', 'interact']
        if any(keyword in name_lower for keyword in interaction_keywords):
            return "interaction"
        
        # Transition behaviors
        transition_keywords = ['move', 'walk', 'jump', 'fall', 'slide']
        if any(keyword in name_lower for keyword in transition_keywords):
            return "transition"
        
        # Default to unknown
        return "unknown"
    
    def _validate_next_behaviors(self, behaviors: Dict[str, BehaviorData]) -> List[str]:
        """
        Validate that referenced next behaviors exist
        
        Args:
            behaviors: Dict of all behaviors
            
        Returns:
            List of warning messages
        """
        warnings = []
        behavior_names = set(behaviors.keys())
        
        for behavior in behaviors.values():
            for next_behavior in behavior.next_behaviors:
                if next_behavior not in behavior_names:
                    warnings.append(f"Behavior '{behavior.name}' references non-existent behavior '{next_behavior}'")
        
        return warnings
    
    def convert_all_sprite_packs(self, assets_dir: str = "assets") -> Dict[str, ConversionResult]:
        """
        Convert all sprite packs in assets directory
        
        Args:
            assets_dir: Path to assets directory
            
        Returns:
            Dict mapping sprite names to ConversionResult
        """
        results = {}
        assets_path = Path(assets_dir)
        
        if not assets_path.exists():
            print(f"❌ Assets directory not found: {assets_path}")
            return results
        
        # Find all sprite pack directories
        sprite_dirs = [d for d in assets_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('.')]
        
        if not sprite_dirs:
            print(f"❌ No sprite packs found in {assets_path}")
            return results
        
        print(f"🔄 Converting {len(sprite_dirs)} sprite pack(s)...")
        
        for sprite_dir in sprite_dirs:
            result = self.convert_sprite_pack(sprite_dir)
            results[sprite_dir.name] = result
            
            if result.success:
                # Write JSON file
                self._write_json_file(result, sprite_dir)
                print(f"✅ {sprite_dir.name}: Converted successfully")
            else:
                print(f"❌ {sprite_dir.name}: Conversion failed")
                for error in result.validation_errors:
                    print(f"  - {error}")
        
        return results
    
    def _write_json_file(self, result: ConversionResult, sprite_path: Path):
        """
        Write conversion result to JSON file
        
        Args:
            result: Conversion result
            sprite_path: Path to sprite pack
        """
        try:
            conf_path = sprite_path / "conf"
            json_path = conf_path / "data.json"
            
            # Prepare JSON data
            json_data = {
                "sprite_name": result.sprite_name,
                "actions": {},
                "behaviors": {}
            }
            
            # Convert actions to dict
            for action_name, action in result.actions.items():
                action_dict = {
                    "name": action.name,
                    "action_type": action.action_type,
                    "animations": {}
                }
                
                if action.border_type:
                    action_dict["border_type"] = action.border_type
                if action.draggable is not None:
                    action_dict["draggable"] = action.draggable
                if action.loop is not None:
                    action_dict["loop"] = action.loop
                
                # Convert animations
                for anim_key, animation in action.animations.items():
                    anim_dict = {
                        "frames": []
                    }
                    
                    if animation.condition:
                        anim_dict["condition"] = animation.condition
                    if animation.priority > 0:
                        anim_dict["priority"] = animation.priority
                    
                    # Convert frames
                    for frame in animation.frames:
                        frame_dict = {
                            "image": frame.image,
                            "duration": frame.duration,
                            "velocity": frame.velocity
                        }
                        
                        if frame.sound:
                            frame_dict["sound"] = frame.sound
                        if frame.volume is not None:
                            frame_dict["volume"] = frame.volume
                        
                        if frame.image_anchor:
                            frame_dict["imageAnchor"] = frame.image_anchor
                        
                        anim_dict["frames"].append(frame_dict)
                    
                    action_dict["animations"][anim_key] = anim_dict
                
                json_data["actions"][action_name] = action_dict
            
            # Convert behaviors to dict
            for behavior_name, behavior in result.behaviors.items():
                behavior_dict = {
                    "name": behavior.name,
                    "frequency": behavior.frequency,
                    "hidden": behavior.hidden,
                    "type": behavior.type
                }
                
                if behavior.condition:
                    behavior_dict["condition"] = behavior.condition
                if behavior.action:
                    behavior_dict["action"] = behavior.action
                if behavior.next_behaviors:
                    behavior_dict["next_behaviors"] = behavior.next_behaviors
                
                json_data["behaviors"][behavior_name] = behavior_dict
            
            # Write to file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            if self.debug_mode:
                print(f"💾 Wrote JSON file: {json_path}")
            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Failed to write JSON file: {e}")
            raise 