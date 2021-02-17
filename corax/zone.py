"""
This module contains all object representing the node the Zone category.
Thats mainly data stuctures.
"""


import corax.context as cctx
from corax.coordinates import to_pixel_position, to_block_position
from corax.pygameutils import render_rect


class Zone():
    """
    The NoGo object is a corax node of the "zone" categorie. It is coordinates
    where the "affected" character are not allowed to go.
    """
    def __init__(self, data):
        self.data = data

    @property
    def script_names(self):
        return self.data.get("scripts", []) or []

    @property
    def name(self):
        return self.data["name"]

    @property
    def type(self):
        return self.data["type"]

    @property
    def zone(self):
        return self.data["zone"]

    @property
    def l(self):
        return self.data["zone"][0]

    @property
    def t(self):
        return self.data["zone"][1]

    @property
    def r(self):
        return self.data["zone"][2]

    @property
    def b(self):
        return self.data["zone"][3]

    @property
    def width(self):
        return self.r - self.l

    @property
    def height(self):
        return self.b - self.t

    def contains(self, block_position=None, pixel_position=None):
        if block_position:
            x, y = block_position
        elif pixel_position:
            x, y = to_block_position(pixel_position)
        else:
            raise ValueError("Zone need at least a position to compare")
        return self.l <= x <= self.r and self.t <= y <= self.b

    @property
    def affect(self):
        return self.data["affect"] or []

    def render(self, screen, camera):
        if cctx.DEBUG is False:
            return
        world_pos = to_pixel_position([self.l, self.t])
        x, y = camera.relative_pixel_position(world_pos)
        w, h = to_pixel_position([self.width, self.height])
        render_rect(screen, (255, 255, 255), x, y, w, h, alpha=25)

    def __repr__(self):
        return f"Zone: {self.name}: {self.l}, {self.r}, {self.t}, {self.b}"