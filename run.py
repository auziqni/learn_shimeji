#!/usr/bin/env python3
"""
Desktop Pet Application Entry Point
==================================

This script provides a user-friendly way to run the desktop pet application.
It handles the module execution properly and provides helpful error messages.

Usage:
    python run.py
"""

import sys
import os
import subprocess

def main():
    """Main entry point for the desktop pet application"""
    
    # Check if we're in the correct directory
    if not os.path.exists('src'):
        print("❌ Error: 'src' directory not found!")
        print("💡 Make sure you're running this from the project root directory.")
        print("📁 Current directory:", os.getcwd())
        return 1
    
    # Check if src/main.py exists
    if not os.path.exists('src/main.py'):
        print("❌ Error: 'src/main.py' not found!")
        print("💡 Make sure the application files are properly installed.")
        return 1
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected!")
        print("💡 It's recommended to activate your virtual environment first:")
        print("   .\\env\\Scripts\\Activate.ps1  # Windows PowerShell")
        print("   source env/bin/activate       # Linux/Mac")
        print()
    
    print("🚀 Starting Desktop Pet Application...")
    print("📋 Using: python -m src.main")
    print()
    
    try:
        # Run the application as a module
        result = subprocess.run([sys.executable, '-m', 'src.main'], 
                              cwd=os.getcwd(),
                              check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Application exited with error code: {e.returncode}")
        return e.returncode
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 