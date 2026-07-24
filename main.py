import os
import sys

# CRITICAL: Change to the directory where this script is located
# This ensures all relative paths (faces/, attendance/, etc.) work
# regardless of how the app is launched (terminal, VS Code, double-click)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create required directories
for directory in ['faces', 'attendance', 'logs', 'screenshots', 'unknown']:
    os.makedirs(directory, exist_ok=True)

import login