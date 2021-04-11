import os
import json

ROOT = None
DEBUG = False
MUTE = False
DATA_FOLDER = None
ANIMATION_FOLDER = None
SET_FOLDER = None
MOVE_FOLDER = None
SCRIPT_FOLDER = None
SCENE_FOLDER = None
SOUNDS_FOLDER = None
GAME_FILE = None
RESOLUTION = None
CAMERA_SPEED = None
FPS = None
BLOCK_SIZE = None
KEY_COLOR = None


def initialize(args):
    """
    This function initialize the engine. This function MUST be called when the
    engine is imported. Nothing works if it is not initialised in a game
    context.
    :args must receive the applications attribute
        args[1] = root of the game file structure.
        --debug, --mute are arguments valids.
    """
    global ROOT, DATA_FOLDER, ANIMATION_FOLDER, SET_FOLDER, MOVE_FOLDER, \
    SCRIPT_FOLDER, SCENE_FOLDER, SOUNDS_FOLDER, GAME_FILE, RESOLUTION, FPS, \
    CAMERA_SPEED, BLOCK_SIZE, KEY_COLOR, DEBUG, MUTE

    ROOT = args[1]
    DEBUG = "--debug" in args or "-d" in args
    MUTE = "--mute" in args or "-m" in args
    ANIMATION_FOLDER = os.path.realpath(os.path.join(ROOT, "animations"))
    SET_FOLDER = os.path.realpath(os.path.join(ROOT, "sets"))
    MOVE_FOLDER = os.path.realpath(os.path.join(ROOT, "moves"))
    SCRIPT_FOLDER = os.path.realpath(os.path.join(ROOT, "scripts"))
    SCENE_FOLDER = os.path.realpath(os.path.join(ROOT, "scenes"))
    SOUNDS_FOLDER = os.path.realpath(os.path.join(ROOT, "sounds"))
    GAME_FILE = os.path.realpath(os.path.join(ROOT, "main.json"))

    with open(os.path.join(ROOT, GAME_FILE), "r") as f:
        game_datas = json.load(f)
    CAMERA_SPEED = game_datas["preferences"]["camera_speed"]
    RESOLUTION = game_datas["preferences"]["resolution"]
    FPS = game_datas["preferences"]["fps"]
    BLOCK_SIZE = game_datas["preferences"]["block_size"]
    KEY_COLOR = game_datas["preferences"]["key_color"]

    return game_datas