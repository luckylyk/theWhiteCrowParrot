

class EVENTS():
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"
    SWITCH_TO = "switch_to"


class ELEMENT_TYPES():
    PLAYER = "player"
    SET_STATIC = "set_static"
    SET_ANIMATED = "set_animated"
    LAYER = "layer"
    PARTICLES = "particles_system"


class SOUND_TYPES():
    AMBIANCE = "ambiance"
    SFX_COLLECTION = "sfx_sound_collection"
    SFX = "sfx_sound"
    MUSIC = "music"

    def __iter__(self):
        yield from [self.AMBIANCE, self.SFX_COLLECTION, self.SFX, self.MUSIC]


class LOOP_TYPES():
    CYCLE = "cycle"
    SHUFFLE = "shuffle"


class PARTICLE_SHAPE_TYPES():
    SQUARE = "square"
    ELLIPSE = "ellipse"
    IMAGE = "image"
    ANIMATION = "animation"