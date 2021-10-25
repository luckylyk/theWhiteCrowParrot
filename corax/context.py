import os

from corax.override import load_json


ROOT = None
DEBUG = False
MUTE = False

TITLE = None
BLOCK_SIZE = None
CAMERA_SPEED = None
FPS = None
GAME_FILE = None
KEY_COLOR = None
RESOLUTION = None

ANIMATION_FOLDER = None
DATA_FOLDER = None
PLAYER_FOLDER = None
SCENE_FOLDER = None
SCRIPT_FOLDER = None
SET_FOLDER = None
SHEET_FOLDER = None
SOUNDS_FOLDER = None
OVERRIDE_FILE = None


def initialize(arguments):
    """
    This function initialize the engine. This function MUST be called when the
    engine is imported. Nothing works if it is not initialised in a game
    context.
    argumenrts: argparse.Namespace
    """
    global ROOT, DATA_FOLDER, ANIMATION_FOLDER, SET_FOLDER, SHEET_FOLDER, \
    SCRIPT_FOLDER, SCENE_FOLDER, SOUNDS_FOLDER, GAME_FILE, RESOLUTION, FPS, \
    CAMERA_SPEED, BLOCK_SIZE, KEY_COLOR, DEBUG, MUTE, PLAYER_FOLDER, TITLE, \
    OVERRIDE_FILE

    ROOT = arguments.game_root
    DEBUG = arguments.debug
    MUTE = arguments.mute

    ANIMATION_FOLDER = os.path.realpath(os.path.join(ROOT, "animations"))
    GAME_FILE = os.path.realpath(os.path.join(ROOT, "main.json"))
    PLAYER_FOLDER = os.path.realpath(os.path.join(ROOT, "players"))
    SCRIPT_FOLDER = os.path.realpath(os.path.join(ROOT, "scripts"))
    SCENE_FOLDER = os.path.realpath(os.path.join(ROOT, "scenes"))
    SET_FOLDER = os.path.realpath(os.path.join(ROOT, "sets"))
    SHEET_FOLDER = os.path.realpath(os.path.join(ROOT, "sheets"))
    SOUNDS_FOLDER = os.path.realpath(os.path.join(ROOT, "sounds"))
    OVERRIDE_FILE = arguments.overrides

    game_data = load_json(os.path.join(ROOT, GAME_FILE))
    TITLE = game_data["title"]
    BLOCK_SIZE = game_data["preferences"]["block_size"]
    CAMERA_SPEED = game_data["preferences"]["camera_speed"]
    FPS = game_data["preferences"]["fps"] * (2 if arguments.speedup else 1)
    KEY_COLOR = game_data["preferences"]["key_color"]
    RESOLUTION = game_data["preferences"]["resolution"]

    return game_data