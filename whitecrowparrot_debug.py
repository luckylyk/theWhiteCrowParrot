import sys
import os
import subprocess

directory = os.path.dirname(os.path.abspath(__file__))
subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "--mute", "--debug"])
