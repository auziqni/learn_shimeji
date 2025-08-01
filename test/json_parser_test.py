#!/usr/bin/env python3
"""
test/json_parser_test.py - Comprehensive Test Suite for JSONParser

Tests all aspects of the JSONParser including:
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
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.json_parser import JSONParser, FrameData, AnimationBlock, ActionData, BehaviorData, ValidationResult


class TestJSONParserComprehensive(unittest.TestCase):
    """Comprehensive test suite for JSONParser"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.assets_dir = self.test_dir / "assets"
        self.assets_dir.mkdir()
        
        # Create test sprite pack structure
        self.test_sprite = self.assets_dir / "TestSprite"
        self.test_sprite.mkdir()
        self.conf_dir = self.test_sprite / "conf"
        self.conf_dir.mkdir()
        
        # Create test image file
        (self.test_sprite / "test.png").touch()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    # ===== BASIC FUNCTIONALITY TESTS =====
    
    def test_basic_initialization(self):
        """Test basic initialization"""
        parser = JSONParser(assets_dir=str(self.assets_dir))
        self.assertEqual(parser.assets_dir, self.assets_dir)
        self.assertEqual(len(parser.sprite_data), 0)
    
    def test_basic_sprite_loading(self):
        """Test basic sprite loading with valid JSON"""
        # Create valid JSON file
        json_data = {
            "metadata": {
                "sprite_name": "TestSprite",
                "conversion_date": "2024-01-01",
                "original_files": ["actions.xml", "behaviors.xml"]
            },
            "actions": {
                "Stay": {
                    "name": "Stay",
                    "action_type": "Stay",
                    "border_type": None,
                    "animations": {
                        "default": {
                            "condition": None,
                            "frames": [
                                {
                                    "image": "test.png",
                                    "duration": 1.0,
                                    "velocity": [0, 0],
                                    "sound": None,
                                    "volume": None
                                }
                            ]
                        }
                    }
                }
            },
            "behaviors": {
                "ChaseMouse": {
                    "name": "ChaseMouse",
                    "frequency": 10,
                    "condition": None,
                    "hidden": False,
                    "next_behaviors": []
                }
            },
            "validation": {
                "success": True,
                "errors": [],
                "warnings": []
            }
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files (for conversion fallback)
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "READY")
        self.assertIn("TestSprite", parser.sprite_data)
    
    # ===== EDGE CASES TESTS =====
    
    def test_missing_json_file(self):
        """Test behavior when JSON file is missing"""
        # Create XML files but no JSON
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        # Should fail because XML files are empty
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "BROKEN")
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format"""
        # Create malformed JSON
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            f.write("{ invalid json }")
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "BROKEN")
    
    def test_missing_required_fields(self):
        """Test handling of JSON with missing required fields"""
        json_data = {
            "actions": {},  # Missing metadata, behaviors, validation
            "behaviors": {}
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "BROKEN")
    
    def test_empty_sprite_directory(self):
        """Test handling of empty sprite directory"""
        empty_sprite = self.assets_dir / "EmptySprite"
        empty_sprite.mkdir()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("EmptySprite", result)
        self.assertEqual(result["EmptySprite"], "BROKEN")
    
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_xml_to_json_conversion_fallback(self):
        """Test XML to JSON conversion when JSON is missing"""
        # Create minimal valid XML files
        actions_xml = self.conf_dir / "actions.xml"
        actions_xml.write_text("""
        <?xml version="1.0" encoding="UTF-8"?>
        <Mascot>
            <ActionList>
                <Action Name="Stay" Type="Stay">
                    <Animation>
                        <Pose Image="test.png" Duration="30" Velocity="0,0"/>
                    </Animation>
                </Action>
            </ActionList>
        </Mascot>
        """)
        
        behaviors_xml = self.conf_dir / "behaviors.xml"
        behaviors_xml.write_text("""
        <?xml version="1.0" encoding="UTF-8"?>
        <Mascot>
            <BehaviorList>
                <Behavior Name="ChaseMouse" Frequency="10"/>
            </BehaviorList>
        </Mascot>
        """)
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        # Should succeed with conversion
        self.assertIn("TestSprite", result)
        self.assertIn("TestSprite", parser.sprite_data)
    
    def test_missing_conf_directory(self):
        """Test handling when conf directory is missing"""
        # Remove conf directory
        shutil.rmtree(self.conf_dir)
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "BROKEN")
    
    # ===== ERROR HANDLING TESTS =====
    
    def test_nonexistent_assets_directory(self):
        """Test handling of nonexistent assets directory"""
        parser = JSONParser(assets_dir="nonexistent")
        result = parser.load_all_sprite_packs()
        
        self.assertEqual(len(result), 0)
    
    def test_permission_errors(self):
        """Test handling of permission errors"""
        # Make directory read-only
        os.chmod(self.assets_dir, 0o444)
        
        try:
            parser = JSONParser(assets_dir=str(self.assets_dir))
            result = parser.load_all_sprite_packs()
            
            # Should handle gracefully
            self.assertIsInstance(result, dict)
        finally:
            # Restore permissions
            os.chmod(self.assets_dir, 0o755)
    
    def test_corrupted_json_data(self):
        """Test handling of corrupted JSON data"""
        json_data = {
            "metadata": {"sprite_name": "TestSprite"},
            "actions": {
                "InvalidAction": {
                    "name": "InvalidAction",
                    "action_type": "InvalidType",
                    "animations": {
                        "default": {
                            "frames": [
                                {
                                    "image": "nonexistent.png",
                                    "duration": "invalid_duration",
                                    "velocity": "invalid_velocity"
                                }
                            ]
                        }
                    }
                }
            },
            "behaviors": {},
            "validation": {"success": True, "errors": [], "warnings": []}
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        # Should handle corrupted data gracefully
        self.assertIn("TestSprite", result)
    
    # ===== VALIDATION TESTS =====
    
    def test_asset_validation(self):
        """Test asset reference validation"""
        json_data = {
            "metadata": {"sprite_name": "TestSprite"},
            "actions": {
                "Stay": {
                    "name": "Stay",
                    "action_type": "Stay",
                    "animations": {
                        "default": {
                            "frames": [
                                {
                                    "image": "test.png",  # Exists
                                    "duration": 1.0,
                                    "velocity": [0, 0]
                                },
                                {
                                    "image": "missing.png",  # Missing
                                    "duration": 1.0,
                                    "velocity": [0, 0]
                                }
                            ]
                        }
                    }
                }
            },
            "behaviors": {},
            "validation": {"success": True, "errors": [], "warnings": []}
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        self.assertIn("TestSprite", result)
        validation_result = parser.sprite_data["TestSprite"]
        self.assertIn("missing.png", validation_result.missing_files)
    
    def test_condition_evaluation(self):
        """Test condition evaluation functionality"""
        parser = JSONParser(assets_dir=str(self.assets_dir))
        
        # Test basic condition evaluation
        sprite_state = {"y": 150, "on_floor": True}
        
        # Test y > 100 condition
        result = parser._evaluate_condition("mascot.y > 100", sprite_state)
        self.assertTrue(result)
        
        # Test y < 100 condition
        result = parser._evaluate_condition("mascot.y < 100", sprite_state)
        self.assertFalse(result)
        
        # Test floor condition
        result = parser._evaluate_condition("mascot.environment.floor.isOn(mascot.anchor)", sprite_state)
        self.assertTrue(result)
    
    # ===== PERFORMANCE TESTS =====
    
    def test_large_json_handling(self):
        """Test handling of large JSON files"""
        # Create large JSON with many actions and behaviors
        json_data = {
            "metadata": {"sprite_name": "TestSprite"},
            "actions": {},
            "behaviors": {},
            "validation": {"success": True, "errors": [], "warnings": []}
        }
        
        # Add many actions
        for i in range(100):
            json_data["actions"][f"Action{i}"] = {
                "name": f"Action{i}",
                "action_type": "Stay",
                "animations": {
                    "default": {
                        "frames": [
                            {
                                "image": "test.png",
                                "duration": 1.0,
                                "velocity": [0, 0]
                            }
                        ]
                    }
                }
            }
        
        # Add many behaviors
        for i in range(50):
            json_data["behaviors"][f"Behavior{i}"] = {
                "name": f"Behavior{i}",
                "frequency": i,
                "condition": None,
                "hidden": False,
                "next_behaviors": []
            }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        result = parser.load_all_sprite_packs()
        
        # Should handle large JSON without issues
        self.assertIn("TestSprite", result)
        self.assertEqual(result["TestSprite"], "READY")
        self.assertEqual(len(parser.sprite_data["TestSprite"].actions), 100)
        self.assertEqual(len(parser.sprite_data["TestSprite"].behaviors), 50)
    
    # ===== DATA STRUCTURE TESTS =====
    
    def test_frame_data_structure(self):
        """Test FrameData structure"""
        frame = FrameData(
            image="test.png",
            duration=1.0,
            velocity=(10, 20),
            sound="test.wav",
            volume=50
        )
        
        self.assertEqual(frame.image, "test.png")
        self.assertEqual(frame.duration, 1.0)
        self.assertEqual(frame.velocity, (10, 20))
        self.assertEqual(frame.sound, "test.wav")
        self.assertEqual(frame.volume, 50)
    
    def test_animation_block_structure(self):
        """Test AnimationBlock structure"""
        frames = [
            FrameData(image="frame1.png", duration=0.5),
            FrameData(image="frame2.png", duration=0.5)
        ]
        
        animation = AnimationBlock(
            condition="mascot.y > 100",
            frames=frames,
            priority=1
        )
        
        self.assertEqual(animation.condition, "mascot.y > 100")
        self.assertEqual(len(animation.frames), 2)
        self.assertEqual(animation.priority, 1)
    
    def test_action_data_structure(self):
        """Test ActionData structure"""
        action = ActionData(
            name="TestAction",
            action_type="Stay",
            border_type="Floor",
            animation_blocks=[],
            default_animation=None
        )
        
        self.assertEqual(action.name, "TestAction")
        self.assertEqual(action.action_type, "Stay")
        self.assertEqual(action.border_type, "Floor")
        self.assertEqual(len(action.animation_blocks), 0)
        self.assertIsNone(action.default_animation)
    
    def test_behavior_data_structure(self):
        """Test BehaviorData structure"""
        behavior = BehaviorData(
            name="TestBehavior",
            frequency=10,
            condition="mascot.y > 100",
            hidden=False,
            next_behaviors=["NextBehavior"]
        )
        
        self.assertEqual(behavior.name, "TestBehavior")
        self.assertEqual(behavior.frequency, 10)
        self.assertEqual(behavior.condition, "mascot.y > 100")
        self.assertFalse(behavior.hidden)
        self.assertEqual(behavior.next_behaviors, ["NextBehavior"])
    
    # ===== INTEGRATION TESTS =====
    
    def test_api_compatibility(self):
        """Test API compatibility with XMLParser"""
        # Create valid JSON
        json_data = {
            "metadata": {"sprite_name": "TestSprite"},
            "actions": {
                "Stay": {
                    "name": "Stay",
                    "action_type": "Stay",
                    "animations": {
                        "default": {
                            "frames": [
                                {
                                    "image": "test.png",
                                    "duration": 1.0,
                                    "velocity": [0, 0]
                                }
                            ]
                        }
                    }
                }
            },
            "behaviors": {
                "ChaseMouse": {
                    "name": "ChaseMouse",
                    "frequency": 10,
                    "condition": None,
                    "hidden": False,
                    "next_behaviors": []
                }
            },
            "validation": {"success": True, "errors": [], "warnings": []}
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        parser.load_all_sprite_packs()
        
        # Test all API methods
        actions = parser.get_actions("TestSprite")
        self.assertIn("Stay", actions)
        
        behaviors = parser.get_behaviors("TestSprite")
        self.assertIn("ChaseMouse", behaviors)
        
        action = parser.get_action("TestSprite", "Stay")
        self.assertIsNotNone(action)
        self.assertEqual(action.name, "Stay")
        
        status = parser.get_sprite_status("TestSprite")
        self.assertEqual(status, "READY")
        
        sprite_names = parser.get_all_sprite_names()
        self.assertIn("TestSprite", sprite_names)
        
        ready_sprites = parser.get_ready_sprite_names()
        self.assertIn("TestSprite", ready_sprites)
    
    def test_condition_based_animation(self):
        """Test condition-based animation selection"""
        json_data = {
            "metadata": {"sprite_name": "TestSprite"},
            "actions": {
                "Stay": {
                    "name": "Stay",
                    "action_type": "Stay",
                    "animations": {
                        "conditional_0": {
                            "condition": "mascot.y > 100",
                            "frames": [
                                {
                                    "image": "high.png",
                                    "duration": 1.0,
                                    "velocity": [0, 0]
                                }
                            ]
                        },
                        "default": {
                            "frames": [
                                {
                                    "image": "low.png",
                                    "duration": 1.0,
                                    "velocity": [0, 0]
                                }
                            ]
                        }
                    }
                }
            },
            "behaviors": {},
            "validation": {"success": True, "errors": [], "warnings": []}
        }
        
        json_path = self.conf_dir / "data.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Create required XML files
        (self.conf_dir / "actions.xml").touch()
        (self.conf_dir / "behaviors.xml").touch()
        
        parser = JSONParser(assets_dir=str(self.assets_dir))
        parser.load_all_sprite_packs()
        
        # Test condition evaluation
        sprite_state_high = {"y": 150}
        frames_high = parser.get_animation_for_condition("TestSprite", "Stay", sprite_state_high)
        self.assertIsNotNone(frames_high)
        self.assertEqual(frames_high[0].image, "high.png")
        
        sprite_state_low = {"y": 50}
        frames_low = parser.get_animation_for_condition("TestSprite", "Stay", sprite_state_low)
        self.assertIsNotNone(frames_low)
        self.assertEqual(frames_low[0].image, "low.png")


if __name__ == "__main__":
    unittest.main(verbosity=2) 