# starter.py - just gets things ready

import sys
import os

# check we can run this thing
def setup():
    print("PC Diagnostic - Setup")
    
    # gotta be windows
    if not sys.platform.startswith('win'):
        print("Sorry, windows only!")
        return False
    
    # python ok?
    if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
        print("Need python 3.6 or better")
        print("You have:", sys.version)
        return False
    
    # check for modules we need
    needed = ['psutil', 'tkinter']
    
    print("\nChecking modules...")
    missing = []
    for mod in needed:
        try:
            if mod == 'tkinter':
                import tkinter  # tkinter is special
            else:
                __import__(mod)
            print(f"  + {mod}")
        except:
            print(f"  - {mod} (missing)")
            missing.append(mod)
    
    # try to get missing ones
    if missing:
        print(f"\nMissing {len(missing)} thing(s)...")
        try:
            import subprocess
            for m in missing:
                if m != 'tkinter':  # can't pip install tkinter
                    print(f"Trying to get {m}...")
                    subprocess.call([sys.executable, '-m', 'pip', 'install', m])
        except Exception as e:
            print(f"Oops: {e}")
            print("\nYou might need to install manually or run as admin")
            resp = input("Try anyway? (y/n): ")
            if resp.lower() != 'y':
                return False
    
    return True


# main bit
if __name__ == "__main__":
    ok = setup()
    
    if ok:
        print("\nAll good! Starting main app...")
        
        # add current folder to path
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if cur_dir not in sys.path:
            sys.path.insert(0, cur_dir)
        
        # try to run the main thing
        try:
            # look for main file
            main_file = os.path.join(cur_dir, 'pc_check.py')
            if os.path.exists(main_file):
                print(f"Found {main_file}")
                
                # import it
                import pc_check
                
                # check if it has what we need
                if hasattr(pc_check, 'main'):
                    pc_check.main()
                else:
                    print("Main file doesn't have main() function")
                    input("Press enter...")
            else:
                print(f"Can't find main file at {main_file}")

                for f in os.listdir(cur_dir):
                    if f.endswith('.py') and 'diag' in f.lower():
                        print(f"Trying {f}...")
                        break
                
                input("Press enter...")
                
        except Exception as e:
            print(f"Failed to start: {e}")
            import traceback
            traceback.print_exc()
            input("\npress enter to quit...")
    else:
        print("\nSetup failed")
        input("Press enter to exit...")
