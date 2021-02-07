import sys
import os
import subprocess

directory = os.path.dirname(os.path.abspath(__file__))
# DEBUG MODE
# subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "--debug", "--mute", "--fullscreen"])
subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "--fullscreen"])
