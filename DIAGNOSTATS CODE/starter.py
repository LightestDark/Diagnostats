#!/usr/bin/env python3

# Quick system checker for the diag tool
# Make sure we can run before opening the main window

import sys
import os
from pathlib import Path

def main():
    print("Checking your system...")
    
    # Windows check
    if sys.platform != "win32":
        print("Oops - this is for Windows only")
        input("Hit enter to quit...")
        return 1
    
    # Python version
    if sys.version_info < (3, 6):
        print("Need Python 3.6 or newer")
        print(f"You have {sys.version}")
        input("Press enter...")
        return 1
    
    # Try to install what's missing
    print("Checking packages...")
    missing = []
    
    # List what we need
    needs = ['psutil', 'wmi', 'tabulate']
    
    for pkg in needs:
        try:
            __import__(pkg)
            print(f"  OK: {pkg}")
        except ImportError:
            print(f"  Missing: {pkg}")
            missing.append(pkg)
    
    if missing:
        print(f"\nNeed to install {len(missing)} packages")
        try:
            import subprocess
            for pkg in missing:
                print(f"Installing {pkg}...")
                # Use pip, hope it works
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print("Done!")
        except Exception as e:
            print(f"Failed: {e}")
            print("\nYou might need to run as admin or install manually:")
            print(f"pip install {' '.join(missing)}")
            input("\nPress enter to try anyway...")
    
    # Now try to run the actual tool
    print("\nStarting diagnostics tool...")
    
    # Look for the main file
    tool_file = "diag_tool.py"
    if not os.path.exists(tool_file):
        # Maybe it's in the same dir?
        tool_file = Path(__file__).parent / "diag_tool.py"
    
    if not os.path.exists(tool_file):
        print(f"Can't find {tool_file}")
        print("Make sure diag_tool.py is in the same folder")
        input("Enter to exit...")
        return 1
    
    # Add current dir to path just in case
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run
        from diag_tool import run_app
        run_app()
    except Exception as e:
        print(f"Error starting tool: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress enter to close...")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
