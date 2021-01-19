import os
import sys

directory = os.path.dirname(os.path.abspath(__file__))
os.system(f'{sys.executable} {directory}/whitecrow {directory}/data')
