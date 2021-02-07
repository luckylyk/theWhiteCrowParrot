"""
This module contains all object representing the node the Zone category.
Thats mainly data stuctures.
"""


import corax.context as cctx
from corax.cordinates import to_pixel_position
from pygameutils import render_rect


class NoGo():
    """
    The NoGo object is a corax node of the "zone" categorie. It is cordinates
    where the "affected" character are not allowed to go.
    """
    def __init__(self, datas):
        self.datas = datas

    @property
    def name(self):
        return self.datas["name"]

    @property
    def type(self):
        return self.datas["type"]

    @property
    def zone(self):
        return self.datas["zone"]

    @property
    def l(self):
        return self.datas["zone"][0]

    @property
    def t(self):
        return self.datas["zone"][1]

    @property
    def r(self):
        return self.datas["zone"][2]

    @property
    def b(self):
        return self.datas["zone"][3]

    @property
    def width(self):
        return self.r - self.l

    @property
    def height(self):
        return self.b - self.t

    def contains(self, block_position):
        x, y = block_position
        return self.l <= x <= self.r and self.t <= y <= self.b

    @property
    def affect(self):
        return self.datas["affect"] or []

    def render(self, screen, camera):
        if cctx.DEBUG is False:
            return
        world_pos = to_pixel_position([self.l, self.t])
        x, y = camera.relative_pixel_position(world_pos)
        w, h = to_pixel_position([self.width, self.height])
        render_rect(screen, (255, 255, 255), x, y, w, h, alpha=25)