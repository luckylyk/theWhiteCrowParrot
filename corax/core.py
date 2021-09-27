"""
This modules contains all constants used in the game file data
"""


class COLORS:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)


class RUN_MODES:
    SCRIPT = "script"
    NORMAL = "normal"
    PAUSE = "pause"
    RESTART = "restart"


class GAMELOOP_ACTIONS:
    RESUME = "resume"
    RESTART = "restart"
    EXIT = "exit"


class MENU_MODES:
    INTERACTIVE = "interactive"
    INACTIVE = "inactive"
    ANIMATED = "animated"


class MENU_EVENTS:
    ENTER = "enter"
    QUIT = "quit"


class EVENTS:
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"
    SWITCH_TO = "switch_to"


class LOOP_TYPES:
    CYCLE = "cycle"
    SHUFFLE = "shuffle"


class SHAPE_TYPES:
    SQUARE = "square"
    ELLIPSE = "ellipse"
    IMAGE = "image"
    ANIMATION = "animation"


class NODE_TYPES:
    # graphics elements
    PLAYER = "player"
    SET_STATIC = "set_static"
    SET_ANIMATED = "set_animated"
    LAYER = "layer"
    PARTICLES = "particles_system"
    # sounds
    AMBIANCE = "ambiance"
    SFX_COLLECTION = "sfx_sound_collection"
    SFX = "sfx_sound"
    MUSIC = "music"
    # zones
    NO_GO = "no_go"
    INTERACTION = "interaction"
