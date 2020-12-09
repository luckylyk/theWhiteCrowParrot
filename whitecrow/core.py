

class COLORS():
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class EVENTS():
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"


class ELEMENT_TYPES():
    PLAYER = "player"
    STATIC = "static"
    LAYER = "layer"
    PARTICLES = "particles_system"


class SOUND_TYPES():
    AMBIANCE = "ambiance"
    SFX_COLLECTION = "sfx_sound_collection"
    SFX = "sfx_sound"


class LOOP_TYPES():
    CYCLE = "cycle"
    SHUFFLE = "shuffle"


class PARTICLE_SHAPE_TYPES():
    SQUARE = "square"
    ELLIPSE = "ellipse"
    IMAGE = "image"
    ANIMATION = "animation"