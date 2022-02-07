import os

from corax.override import load_json


ROOT = None
OVERRIDE_FILE = None

DEBUG = False
MUTE = False

BLOCK_SIZE = None
CAMERA_SPEED = None
FPS = None
GAME_FILE = None
KEY_COLOR = None
RESOLUTION = None
TITLE = None

ANIMATION_FOLDER = None
CHARACTER_FOLDER = None
MENU_FOLDER = None
DATA_FOLDER = None
RELATIONSHIP_FOLDER = None
SCENE_FOLDER = None
SCRIPT_FOLDER = None
SET_FOLDER = None
SHEET_FOLDER = None
SOUNDS_FOLDER = None


def initialize(arguments):
    """
    This function initialize the engine. This function MUST be called when the
    engine is imported. Nothing works if it is not initialised in a game
    context.
    argumenrts: argparse.Namespace
    """
    global ROOT, DATA_FOLDER, ANIMATION_FOLDER, SET_FOLDER, SHEET_FOLDER, \
    SCRIPT_FOLDER, SCENE_FOLDER, SOUNDS_FOLDER, GAME_FILE, RESOLUTION, FPS, \
    CAMERA_SPEED, BLOCK_SIZE, KEY_COLOR, DEBUG, MUTE, CHARACTER_FOLDER, TITLE, \
    OVERRIDE_FILE, RELATIONSHIP_FOLDER, MENU_FOLDER

    ROOT = os.path.abspath(arguments.game_root)
    OVERRIDE_FILE = arguments.overrides

    DEBUG = arguments.debug
    MUTE = arguments.mute

    ANIMATION_FOLDER = os.path.realpath(os.path.join(ROOT, "animations"))
    CHARACTER_FOLDER = os.path.realpath(os.path.join(ROOT, "characters"))
    MENU_FOLDER = os.path.realpath(os.path.join(ROOT, "menus"))
    GAME_FILE = os.path.realpath(os.path.join(ROOT, "main.json"))
    RELATIONSHIP_FOLDER = os.path.realpath(os.path.join(ROOT, "relationships"))
    SCRIPT_FOLDER = os.path.realpath(os.path.join(ROOT, "scripts"))
    SCENE_FOLDER = os.path.realpath(os.path.join(ROOT, "scenes"))
    SET_FOLDER = os.path.realpath(os.path.join(ROOT, "sets"))
    SHEET_FOLDER = os.path.realpath(os.path.join(ROOT, "sheets"))
    SOUNDS_FOLDER = os.path.realpath(os.path.join(ROOT, "sounds"))

    game_data = load_json(os.path.join(ROOT, GAME_FILE))
    TITLE = game_data["title"]
    BLOCK_SIZE = game_data["preferences"]["block_size"]
    CAMERA_SPEED = game_data["preferences"]["camera_speed"]
    FPS = game_data["preferences"]["fps"] * (2 if arguments.speedup else 1)
    KEY_COLOR = game_data["preferences"]["key_color"]
    RESOLUTION = game_data["preferences"]["resolution"]

    return game_data