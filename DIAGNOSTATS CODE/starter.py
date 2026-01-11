# starter.py
import os
import sys
import subprocess
import platform

def check_and_install():
    """Check and install required packages"""
    print("Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("ERROR: Python 3.6 or higher is required")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if it's Windows
    if platform.system() != "Windows":
        print("ERROR: This tool is for Windows only")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Required packages
    packages = ["psutil", "wmi", "tabulate", "py-cpuinfo"]
    
    print("\nChecking required packages...")
    missing = []
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\nInstalling {len(missing)} missing packages...")
        try:
            for package in missing:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("\n✓ All packages installed successfully!")
        except Exception as e:
            print(f"\nERROR: Failed to install packages: {e}")
            print("\nPlease install manually: pip install psutil wmi tabulate py-cpuinfo")
            input("\nPress Enter to exit...")
            sys.exit(1)
    
    # Check for Tkinter (should be included with Python)
    try:
        import tkinter
        print("✓ tkinter")
    except ImportError:
        print("\nERROR: Tkinter is not available")
        print("Tkinter should be included with Python installation.")
        print("Reinstall Python and make sure to check 'tcl/tk and IDLE' option.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    return True

def run_diagnostic():
    """Run the diagnostic tool"""
    print("\n" + "="*50)
    print("Starting Windows Diagnostic Tool...")
    print("="*50 + "\n")
    
    try:
        # Import and run the main tool
        from diagnostic_tool import main
        main()
    except Exception as e:
        print(f"\nERROR: Failed to start diagnostic tool: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    if check_and_install():
        run_diagnostic()