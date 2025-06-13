import os
import sys
import subprocess

def open_cv_details(path: str) -> bool:
    if not os.path.exists(path):
        print(f"Error: File not found at path '{path}'")
        return False

    try:
        # Platform-specific commands to open files
        if sys.platform == "win32":
            # Windows
            os.startfile(path)
        elif sys.platform == "darwin": 
            # macOS
            subprocess.run(["open", path], check=True)
        else:
            # Linux
            subprocess.run(["xdg-open", path], check=True)
        
        print(f"Successfully executed command to open '{path}'")
        return True
    
    except Exception as e:
        print(f"Failed to open file: {e}")
        return False