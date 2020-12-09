import os


ROOT = None
DATA_FOLDER = None
ANIMATION_FOLDER = None
SET_FOLDER = None
MOVE_FOLDER = None
SCENE_FOLDER = None
SOUNDS_FOLDER = None
GAME_FILE = None


def populate(root):
    global ROOT, DATA_FOLDER, ANIMATION_FOLDER, SET_FOLDER, MOVE_FOLDER,\
    SCENE_FOLDER, SOUNDS_FOLDER, GAME_FILE

    ROOT = root
    ANIMATION_FOLDER = os.path.join(ROOT, "animations")
    SET_FOLDER = os.path.join(ROOT, "sets")
    MOVE_FOLDER = os.path.join(ROOT, "moves")
    SCENE_FOLDER = os.path.join(ROOT, "scenes")
    SOUNDS_FOLDER = os.path.join(ROOT, "sounds")
    GAME_FILE = os.path.join(ROOT, "main.json")