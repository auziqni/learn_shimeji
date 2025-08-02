#!/usr/bin/env python3
"""
test/run_xml2json.py - XML to JSON Converter Runner

Default: Convert all sprite packs in assets directory
With parameter: Convert specific sprite pack by name
Usage: python run_xml2json.py [sprite_name]
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.xml2json import XML2JSONConverter


def main():
    """Main function to run XML to JSON conversion"""
    # Check if sprite name is provided as argument
    if len(sys.argv) > 1:
        sprite_name = sys.argv[1]
        convert_single_sprite(sprite_name)
    else:
        convert_all_sprites()


def convert_single_sprite(sprite_name):
    """Convert a single sprite pack"""
    print(f"🔄 Converting {sprite_name}...")
    
    # Initialize converter
    converter = XML2JSONConverter(
        write_existing=True,
        debug_mode=True
    )
    
    # Check if sprite exists
    sprite_path = Path("assets") / sprite_name
    if not sprite_path.exists():
        print(f"❌ Sprite pack '{sprite_name}' not found in assets/")
        print("Available sprites:")
        list_available_sprites()
        sys.exit(1)
    
    # Convert single sprite pack
    result = converter.convert_sprite_pack(sprite_path)
    
    # Print results
    if result.success:
        print(f"✅ {sprite_name} converted successfully!")
        print(f"   Actions: {len(result.actions)}")
        print(f"   Behaviors: {len(result.behaviors)}")
        
        if result.warnings:
            print(f"   Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"     - {warning}")
    else:
        print(f"❌ Failed to convert {sprite_name}")
        for error in result.validation_errors:
            print(f"   Error: {error}")
        sys.exit(1)


def convert_all_sprites():
    """Convert all sprite packs"""
    print("🚀 XML to JSON Converter")
    print("=" * 40)
    
    # Initialize converter
    converter = XML2JSONConverter(
        write_existing=True,
        debug_mode=True
    )
    
    # Convert all sprite packs
    print("📁 Converting sprite packs in assets/ directory...")
    results = converter.convert_all_sprite_packs()
    
    # Print summary
    print("\n📊 Conversion Summary:")
    print("=" * 40)
    
    successful = sum(1 for r in results.values() if r.success)
    total = len(results)
    
    print(f"Total sprite packs: {total}")
    print(f"Successful conversions: {successful}")
    print(f"Failed conversions: {total - successful}")
    print()
    
    # Print detailed results
    for sprite_name, result in results.items():
        status = "✅" if result.success else "❌"
        print(f"{status} {sprite_name}")
        print(f"   Actions: {len(result.actions)}")
        print(f"   Behaviors: {len(result.behaviors)}")
        
        if result.validation_errors:
            print(f"   Errors: {len(result.validation_errors)}")
            for error in result.validation_errors:
                print(f"     - {error}")
        
        if result.warnings:
            print(f"   Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"     - {warning}")
        print()
    
    # Final status
    if successful == total:
        print("🎉 All conversions completed successfully!")
    else:
        print(f"⚠️  {total - successful} conversion(s) failed. Check errors above.")
    
    return 0 if successful == total else 1


def list_available_sprites():
    """List all available sprite packs"""
    assets_path = Path("assets")
    if not assets_path.exists():
        print("   No assets directory found")
        return
    
    sprites = [d.name for d in assets_path.iterdir() if d.is_dir()]
    if not sprites:
        print("   No sprite packs found in assets/")
        return
    
    for sprite in sprites:
        print(f"   - {sprite}")


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Conversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 