import sys
import subprocess

try:
    import pygame
except ImportError:
    subprocess.call([sys.executable, "-m", "-pip", "-install", "pygame"])


import os


directory = os.path.dirname(os.path.abspath(__file__))
subprocess.call([sys.executable, f"{directory}/corax", f"{directory}/whitecrowparrot", "-f", "-s"])
