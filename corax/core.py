"""
This modules contains all constants used in the game file data
"""


class AIM_RELATIONSHIP_TYPES:
    FACING = "facing"
    BACK_TO_BACK = "back_to_back"
    SUBJECT_FROM_BEHIND = "subject_from_behind"
    TARGET_FROM_BEHIND = "target_from_behind"


class CHARACTER_TYPES:
    PLAYER = "player"
    NPC = "npc"


class COLORS:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)


class EVENTS:
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"
    SWITCH_TO = "switch_to"


class GAMELOOP_ACTIONS:
    RESUME = "resume"
    RESTART = "restart"
    EXIT = "exit"


class LOOP_TYPES:
    CYCLE = "cycle"
    SHUFFLE = "shuffle"


class MENU_MODES:
    INTERACTIVE = "interactive"
    INACTIVE = "inactive"
    ANIMATED = "animated"


class MENU_EVENTS:
    ENTER = "enter"
    QUIT = "quit"


class NODE_TYPES:
    # graphics elements
    PLAYER = "player"
    NPC = "npc"
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
    RELATIONSHIP = "relationship"
    COLLIDER = "collider"
    EVENT_ZONE = "event_zone"


class RUN_MODES:
    SCRIPT = "script"
    NORMAL = "normal"
    PAUSE = "pause"
    RESTART = "restart"
    RESTORE_CHECKPOINT = "restore_checkpoint"


class SHAPE_TYPES:
    SQUARE = "square"
    ELLIPSE = "ellipse"
    IMAGE = "image"
    ANIMATION = "animation"
