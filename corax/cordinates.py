
import corax.context as cctx


class Cordinates():
    def __init__(
            self, mirror=False,
            block_position=None,
            pixel_offset=None,
            center=None):
        self.mirror = False
        self.pixel_offset = pixel_offset or [0, 0]
        self.block_position = block_position or [0, 0]
        self.center_offset = center or [0, 0]
        self.elevation = 0

    @property
    def pixel_position(self):
        block = cctx.BLOCK_SIZE
        x = (self.block_position[0] * block) + self.pixel_offset[0]
        y = (self.block_position[1] * block) + self.pixel_offset[1]
        return x, y

    @property
    def pixel_center(self):
        pixel_position = self.pixel_position
        x = pixel_position[0] + self.center_offset[0]
        y = pixel_position[1] + self.center_offset[1]
        return [x, y]