"""
This modules contains all constants used in the game file datas
"""

class RUN_MODE():
    SCRIPT = "script"
    NORMAL = "normal"
    PAUSE = "pause"


class EVENTS():
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"
    SWITCH_TO = "switch_to"


class LOOP_TYPES():
    CYCLE = "cycle"
    SHUFFLE = "shuffle"


class SHAPE_TYPES():
    SQUARE = "square"
    ELLIPSE = "ellipse"
    IMAGE = "image"
    ANIMATION = "animation"


class NODE_TYPES():
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
