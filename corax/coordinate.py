
"""
Module to give some tool to handle and convert 2d coordinates data
"""


import math
import corax.context as cctx


class Coordinate():
    """
    This object represent the coordinate system used for each localised element
    in the scene.
    """
    def __init__(
            self, flip=False,
            block_position=None,
            pixel_offset=None,
            center=None):
        self.flip = False
        self.pixel_offset = pixel_offset or [0, 0]
        self.block_position = block_position or [0, 0]
        self.center_offset = center or [0, 0]
        self.deph = 0

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
