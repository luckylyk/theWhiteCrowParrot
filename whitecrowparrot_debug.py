import sys
import os
import subprocess

directory = os.path.dirname(os.path.abspath(__file__))
subprocess.call([
    sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot",
    "--speedup", "--scaled",  "--mute", "--debug", "--overrides",
    "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot/overrides/hole.ovr"])
