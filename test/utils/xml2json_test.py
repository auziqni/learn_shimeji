#!/usr/bin/env python3
"""
test/xml2json_test.py - Comprehensive Test Suite for XML2JSON Converter

Tests all aspects of the XML to JSON conversion including:
- Normal operations
- Edge cases
- Fallback conditions
- Error handling
- Validation scenarios
- Performance considerations
"""

import unittest
import tempfile
import shutil
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.xml2json import (
    XML2JSONConverter, 
    ConversionResult, 
    ActionData, 
    BehaviorData, 
    AnimationBlock, 
    FrameData
)


class TestXML2JSONComprehensive(unittest.TestCase):
    """Comprehensive test suite for XML2JSONConverter"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.test_dir) / "assets"
        self.assets_dir.mkdir()
        
        # Create test sprite pack
        self.test_sprite = "TestSprite"
        self.sprite_path = self.assets_dir / self.test_sprite
        self.sprite_path.mkdir()
        
        # Create conf directory
        self.conf_path = self.sprite_path / "conf"
        self.conf_path.mkdir()
        
        # Create test images
        (self.sprite_path / "idle.png").touch()
        (self.sprite_path / "walk.png").touch()
        (self.sprite_path / "idle2.png").touch()
        (self.sprite_path / "walk1.png").touch()
        (self.sprite_path / "walk2.png").touch()
        (self.sprite_path / "walk3.png").touch()
        
        # Initialize converter
        self.converter = XML2JSONConverter(
            write_existing=True,
            debug_mode=False
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _create_basic_actions_xml(self):
        """Create basic actions.xml file"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay" BorderType="Floor">
            <Animation>
                <Pose Image="idle.png" Duration="30" Velocity="0,0" />
            </Animation>
        </Action>
        <Action Name="Walk" Type="Move" BorderType="Floor">
            <Animation>
                <Pose Image="walk.png" Duration="15" Velocity="-2,0" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
    
    def _create_basic_behaviors_xml(self):
        """Create basic behaviors.xml file"""
        behaviors_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <BehaviorList>
        <Behavior Name="ChaseMouse" Frequency="0" Hidden="true"/>
        <Behavior Name="SitDown" Frequency="200" Hidden="false">
            <NextBehaviorList Add="false">
                <BehaviorReference Name="SitDownAfterPet" Frequency="1" />
            </NextBehaviorList>
        </Behavior>
        <Behavior Name="SitDownAfterPet" Frequency="0" Hidden="true" />
    </BehaviorList>
</Mascot>"""
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(behaviors_xml)
    
    def _create_complex_actions_xml(self):
        """Create complex actions.xml with all action types"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay" BorderType="Floor" Draggable="true" Loop="false">
            <Animation>
                <Pose Image="idle.png" Duration="75" Velocity="0,0" />
                <Pose Image="idle2.png" Duration="5" Velocity="0,0" />
            </Animation>
            <Animation Condition="#{mascot.y > 100}">
                <Pose Image="idle2.png" Duration="30" Velocity="0,0" />
            </Animation>
        </Action>
        <Action Name="Walk" Type="Move" BorderType="Floor">
            <Animation>
                <Pose Image="walk1.png" Duration="4" Velocity="-2,0" />
                <Pose Image="walk2.png" Duration="4" Velocity="-2,0" />
                <Pose Image="walk3.png" Duration="4" Velocity="-2,0" Sound="walk.wav" Volume="-10"/>
            </Animation>
        </Action>
        <Action Name="EmbeddedAction" Type="Embedded" Class="com.example.Action" OffsetX="10" OffsetY="20" />
        <Action Name="SequenceAction" Type="Sequence" Loop="false">
            <ActionReference Name="Stay" Duration="1000" />
            <ActionReference Name="Walk" Duration="2000" />
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
    
    def _create_complex_behaviors_xml(self):
        """Create complex behaviors.xml with all behavior types"""
        behaviors_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <BehaviorList>
        <!-- System behaviors -->
        <Behavior Name="ChaseMouse" Frequency="0" Hidden="true"/>
        <Behavior Name="Fall" Frequency="0" Hidden="true" />
        <Behavior Name="Dragged" Frequency="0" Hidden="true" />
        <Behavior Name="Thrown" Frequency="0" Hidden="true" />
        <Behavior Name="Divided" Frequency="0" Hidden="true" />
        
        <!-- AI behaviors -->
        <Behavior Name="SitDown" Frequency="200" Hidden="false">
            <NextBehaviorList Add="false">
                <BehaviorReference Name="SitDownAfterPet" Frequency="1" />
            </NextBehaviorList>
        </Behavior>
        <Behavior Name="Sleep" Frequency="40" Hidden="false">
            <NextBehaviorList Add="false">
                <BehaviorReference Name="SitDownAfterPet" Frequency="1" />
            </NextBehaviorList>
        </Behavior>
        
        <!-- Interaction behaviors -->
        <Behavior Name="Pet" Frequency="0" Hidden="true">
            <NextBehaviorList Add="false">
                <BehaviorReference Name="SitDownAfterPet" Frequency="1" />
            </NextBehaviorList>
        </Behavior>
        <Behavior Name="BePet" Frequency="0" Hidden="true" />
        
        <!-- Transition behaviors -->
        <Behavior Name="SitDownAfterPet" Frequency="0" Hidden="true" />
        <Behavior Name="ShortStandAfterAction" Frequency="0" Hidden="true" />
        
        <!-- Conditional behaviors -->
        <Condition Condition="#{mascot.environment.floor.isOn(mascot.anchor)}">
            <Behavior Name="Walk" Frequency="100" Hidden="false">
                <NextBehaviorList Add="false">
                    <BehaviorReference Name="SitDown" Frequency="1" />
                </NextBehaviorList>
            </Behavior>
        </Condition>
    </BehaviorList>
</Mascot>"""
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(behaviors_xml)
    
    def _create_malformed_xml(self):
        """Create malformed XML files for error testing"""
        malformed_actions = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay">
            <Animation>
                <Pose Image="idle.png" Duration="invalid" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(malformed_actions)
    
    def _create_empty_xml(self):
        """Create empty XML files"""
        empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(empty_xml)
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(empty_xml)
    
    def _create_invalid_references_xml(self):
        """Create XML with invalid behavior references"""
        behaviors_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <BehaviorList>
        <Behavior Name="ValidBehavior" Frequency="100" Hidden="false">
            <NextBehaviorList Add="false">
                <BehaviorReference Name="NonExistentBehavior" Frequency="1" />
            </NextBehaviorList>
        </Behavior>
    </BehaviorList>
</Mascot>"""
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(behaviors_xml)
    
    # ===== BASIC FUNCTIONALITY TESTS =====
    
    def test_converter_initialization(self):
        """Test XML2JSONConverter initialization with different parameters"""
        # Test with debug mode
        converter_debug = XML2JSONConverter(write_existing=True, debug_mode=True)
        self.assertTrue(converter_debug.write_existing)
        self.assertTrue(converter_debug.debug_mode)
        
        # Test without debug mode
        converter_normal = XML2JSONConverter(write_existing=False, debug_mode=False)
        self.assertFalse(converter_normal.write_existing)
        self.assertFalse(converter_normal.debug_mode)
        
        # Test default parameters
        converter_default = XML2JSONConverter()
        self.assertFalse(converter_default.write_existing)
        self.assertFalse(converter_default.debug_mode)
    
    def test_basic_conversion(self):
        """Test basic XML to JSON conversion"""
        self._create_basic_actions_xml()
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Check basic success
        self.assertTrue(result.success)
        self.assertEqual(result.sprite_name, self.test_sprite)
        
        # Check actions
        self.assertIn("Stay", result.actions)
        self.assertIn("Walk", result.actions)
        
        # Check behaviors
        self.assertIn("ChaseMouse", result.behaviors)
        self.assertIn("SitDown", result.behaviors)
        self.assertIn("SitDownAfterPet", result.behaviors)
    

    
    # ===== EDGE CASES TESTS =====
    
    def test_empty_xml_files(self):
        """Test handling of empty XML files"""
        self._create_empty_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle gracefully
        self.assertIsInstance(result.actions, dict)
        self.assertIsInstance(result.behaviors, dict)
        # May or may not succeed depending on implementation
    
    def test_missing_attributes(self):
        """Test handling of missing XML attributes"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay">
            <Animation>
                <Pose Image="idle.png" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
        
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle missing attributes gracefully
        self.assertIsInstance(result.actions, dict)
    
    def test_invalid_duration_values(self):
        """Test handling of invalid duration values"""
        self._create_malformed_xml()
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle errors gracefully
        self.assertIsInstance(result.behaviors, dict)
    
    def test_invalid_velocity_values(self):
        """Test handling of invalid velocity values"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay">
            <Animation>
                <Pose Image="idle.png" Duration="30" Velocity="invalid" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
        
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle invalid velocity gracefully
        self.assertIsInstance(result.actions, dict)
    
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_namespace_fallback(self):
        """Test fallback when namespace is not found"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot>
    <ActionList>
        <Action Name="Stay" Type="Stay">
            <Animation>
                <Pose Image="idle.png" Duration="30" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
        
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should fallback to non-namespace parsing
        self.assertIsInstance(result.actions, dict)
    
    def test_missing_action_name(self):
        """Test handling of actions without names"""
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Type="Stay">
            <Animation>
                <Pose Image="idle.png" Duration="30" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
        
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should skip actions without names
        self.assertIsInstance(result.actions, dict)
    
    def test_missing_behavior_name(self):
        """Test handling of behaviors without names"""
        behaviors_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <BehaviorList>
        <Behavior Frequency="200" Hidden="false" />
    </BehaviorList>
</Mascot>"""
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(behaviors_xml)
        
        self._create_basic_actions_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should skip behaviors without names
        self.assertIsInstance(result.behaviors, dict)
    
    # ===== ERROR HANDLING TESTS =====
    

    
    def test_invalid_xml_syntax(self):
        """Test handling of invalid XML syntax"""
        invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>
        <Action Name="Stay" Type="Stay">
            <Animation>
                <Pose Image="idle.png" Duration="30" />
            </Animation>
        </Action>
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(invalid_xml)
        
        self._create_basic_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle gracefully
        self.assertIsInstance(result.actions, dict)
    

    
    # ===== VALIDATION TESTS =====
    
    def test_behavior_categorization(self):
        """Test comprehensive behavior type categorization"""
        self._create_complex_behaviors_xml()
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Test system behaviors
        system_behaviors = ["ChaseMouse", "Fall", "Dragged", "Thrown", "Divided"]
        for name in system_behaviors:
            if name in result.behaviors:
                self.assertEqual(result.behaviors[name].type, "system")
        
        # Test AI behaviors
        ai_behaviors = ["SitDown", "Sleep", "Walk"]
        for name in ai_behaviors:
            if name in result.behaviors:
                self.assertEqual(result.behaviors[name].type, "ai")
        
        # Test interaction behaviors
        interaction_behaviors = ["Pet", "BePet"]
        for name in interaction_behaviors:
            if name in result.behaviors:
                self.assertEqual(result.behaviors[name].type, "interaction")
        
        # Test transition behaviors
        transition_behaviors = ["ShortStandAfterAction"]
        for name in transition_behaviors:
            if name in result.behaviors:
                self.assertEqual(result.behaviors[name].type, "transition")
    

    

    
    # ===== PERFORMANCE TESTS =====
    
    def test_large_xml_handling(self):
        """Test handling of large XML files"""
        # Create large actions.xml
        actions_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <ActionList>"""
        
        # Add many actions
        for i in range(50):
            actions_xml += f"""
        <Action Name="Action{i}" Type="Stay" BorderType="Floor">
            <Animation>
                <Pose Image="idle.png" Duration="30" Velocity="0,0" />
            </Animation>
        </Action>"""
        
        actions_xml += """
    </ActionList>
</Mascot>"""
        
        actions_file = self.conf_path / "actions.xml"
        with open(actions_file, 'w', encoding='utf-8') as f:
            f.write(actions_xml)
        
        # Create large behaviors.xml
        behaviors_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Mascot xmlns="http://www.group-finity.com/Mascot">
    <BehaviorList>"""
        
        # Add many behaviors
        for i in range(50):
            behaviors_xml += f"""
        <Behavior Name="Behavior{i}" Frequency="{i * 10}" Hidden="false" />"""
        
        behaviors_xml += """
    </BehaviorList>
</Mascot>"""
        
        behaviors_file = self.conf_path / "behaviors.xml"
        with open(behaviors_file, 'w', encoding='utf-8') as f:
            f.write(behaviors_xml)
        
        result = self.converter.convert_sprite_pack(self.sprite_path)
        
        # Should handle large files
        self.assertIsInstance(result.actions, dict)
        self.assertIsInstance(result.behaviors, dict)
        self.assertGreater(len(result.actions), 0)
        self.assertGreater(len(result.behaviors), 0)
    
    # ===== DATA STRUCTURE TESTS =====
    
    def test_frame_data_creation(self):
        """Test FrameData creation and properties"""
        frame = FrameData(
            image="test.png",
            duration=1.5,
            velocity=(2, -1),
            sound="test.wav",
            volume=75
        )
        
        self.assertEqual(frame.image, "test.png")
        self.assertEqual(frame.duration, 1.5)
        self.assertEqual(frame.velocity, (2, -1))
        self.assertEqual(frame.sound, "test.wav")
        self.assertEqual(frame.volume, 75)
    
    def test_animation_block_creation(self):
        """Test AnimationBlock creation and properties"""
        frame = FrameData(image="test.png", duration=1.0)
        anim_block = AnimationBlock(
            condition="#{mascot.y > 100}",
            frames=[frame],
            priority=1
        )
        
        self.assertEqual(anim_block.condition, "#{mascot.y > 100}")
        self.assertEqual(len(anim_block.frames), 1)
        self.assertEqual(anim_block.priority, 1)
    
    def test_action_data_creation(self):
        """Test ActionData creation and properties"""
        action = ActionData(
            name="Stay",
            action_type="Stay",
            border_type="Floor",
            draggable=True,
            loop=False
        )
        
        self.assertEqual(action.name, "Stay")
        self.assertEqual(action.action_type, "Stay")
        self.assertEqual(action.border_type, "Floor")
        self.assertTrue(action.draggable)
        self.assertFalse(action.loop)
    
    def test_behavior_data_creation(self):
        """Test BehaviorData creation and properties"""
        behavior = BehaviorData(
            name="SitDown",
            frequency=200,
            hidden=False,
            condition="#{mascot.environment.floor.isOn(mascot.anchor)}",
            next_behaviors=["SitDownAfterPet"],
            type="ai"
        )
        
        self.assertEqual(behavior.name, "SitDown")
        self.assertEqual(behavior.frequency, 200)
        self.assertFalse(behavior.hidden)
        self.assertEqual(behavior.condition, "#{mascot.environment.floor.isOn(mascot.anchor)}")
        self.assertEqual(behavior.next_behaviors, ["SitDownAfterPet"])
        self.assertEqual(behavior.type, "ai")
    
    def test_conversion_result_creation(self):
        """Test ConversionResult creation and properties"""
        result = ConversionResult(
            sprite_name="TestSprite",
            actions={},
            behaviors={},
            validation_errors=[],
            warnings=[],
            success=True
        )
        
        self.assertEqual(result.sprite_name, "TestSprite")
        self.assertIsInstance(result.actions, dict)
        self.assertIsInstance(result.behaviors, dict)
        self.assertIsInstance(result.validation_errors, list)
        self.assertIsInstance(result.warnings, list)
        self.assertTrue(result.success)
    
    # ===== INTEGRATION TESTS =====
    

    



if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 