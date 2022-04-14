import os
import sys
import json
import pygame
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

sheet_folder = os.path.join(os.path.dirname(__file__), "../../../whitecrowparrot/sheets")
files = os.listdir(sheet_folder)
sheets = [os.path.join(sheet_folder, f) for f in files if f.endswith(".json")]
files = [f for f in os.listdir(sheet_folder) if f not in files]
sheets.extend([os.path.join(sheet_folder, f) for f in files if f.endswith(".json")])
for sheet in sheets:
    print(sheet)

import corax.context as cctx
game_folder = os.path.join(os.path.dirname(__file__), "../../..", "whitecrowparrot")
print (game_folder)


class MockArguments:
    """
    The Corax Engine uses an argparse object to initialize. This is a argparse
    mocker to be able to initialize the engine for sdk uses.
    """
    game_root = game_folder
    debug = False
    mute = True
    speedup = False
    overrides = None


cctx.initialize(MockArguments)
from corax.pygameutils import load_frames

pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()
pygame.display.set_mode(cctx.RESOLUTION)

images = []
for sheet in sheets:
    with open(sheet, "r") as f:
        data = json.load(f)
    images_path = os.path.join(cctx.ANIMATION_FOLDER, [str(k) for k in data["layers"].values()][0])
    print (images_path)
    images.extend(load_frames(images_path, data["frame_size"], data["key_color"]))

print (len(images))
