import sys
import os
import subprocess

directory = os.path.dirname(os.path.abspath(__file__))
# DEBUG MODE COMMAND
subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "--debug", "--mute"])
# NORMAL MODE COMMAND
# subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "--fullscreen"])
