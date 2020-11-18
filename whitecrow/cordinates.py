from whitecrow.prefs import OPTIONS


class Cordinates():
    def __init__(self, mirror=False, position=None, pixel_offset=None):
        self.mirror = False
        self.pixel_offset = pixel_offset or [0, 0]
        self.position = position or [0, 0]

    def world_position(self):
        x = (self.position[0] * OPTIONS["grid_size"]) + self.pixel_offset[0]
        y = (self.position[1] * OPTIONS["grid_size"]) + self.pixel_offset[1]
        return x, y
