"""
Module to give some tool to handle and convert 2d coordinates data
"""

import corax.context as cctx
from corax.euclide import distance2d
from corax.mathutils import sum_num_arrays


class Coordinate():
    """
    This object represent the coordinate system used for each localised element
    in the scene.
    """

    def __init__(
            self,
            flip=False,
            block_position=None,
            pixel_position=None,
            center=None):

        self.flip = flip

        if not pixel_position:
            self.block_position = block_position or [0, 0]
            self.pixel_offset = [0, 0]
        else:
            self.block_position = to_block_position(pixel_position)
            self.pixel_offset = extract_pixel_offset(pixel_position)

        self.center_offset = center or [0, 0]
        self.deph = 0

    def block_center_distance(self, cordinate):
        pixel_distance = distance2d(self.pixel_center, cordinate.pixel_center)
        return pixel_distance // cctx.BLOCK_SIZE

    def offset(self, block_offset=None, pixel_offset=None):
        pixel_offset = pixel_offset or [0, 0]

        if block_offset:
            position = to_pixel_position(block_offset)
            pixel_offset = sum_num_arrays(pixel_offset, position)

        if self.flip:
            pixel_offset = flip_position(pixel_offset)

        block_offset = to_block_position(pixel_offset)
        pixel_offset = extract_pixel_offset(pixel_offset)

        block_position = sum_num_arrays(
            self.block_position, block_offset)
        self.block_position = block_position
        self.pixel_offset = sum_num_arrays(
            self.pixel_offset, pixel_offset)

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


def aim_target(position, flip, target):
    left_right = position[0] < target[0]
    return (left_right and not flip) or (not left_right and flip)


def to_block_position(pixel_position):
    x = pixel_position[0] // cctx.BLOCK_SIZE
    y = pixel_position[1] // cctx.BLOCK_SIZE
    return x, y


def to_block_size(size):
    x = (size[0] // cctx.BLOCK_SIZE) - 1
    y = (size[1] // cctx.BLOCK_SIZE) - 1
    return x, y


def to_pixel_position(block_position):
    x = block_position[0] * cctx.BLOCK_SIZE
    y = block_position[1] * cctx.BLOCK_SIZE
    return x, y


def flip_position(position):
    """
    Flip only horizontal posisition (x)
    """
    return -position[0], position[1]


def map_pixel_position(pixel_position, size=None, flip=False):
    """
    Map a pixel_position to a image if the coordinates are horizontally fliped
    """
    if flip is False:
        return pixel_position
    return [size[0] - pixel_position[0], pixel_position[1]]


def extract_pixel_offset(pixel_position):
    """
    Extract pixel offset. Subustract block position and returns the rest.
    """
    return (
        pixel_position[0] % cctx.BLOCK_SIZE,
        pixel_position[1] % cctx.BLOCK_SIZE)
