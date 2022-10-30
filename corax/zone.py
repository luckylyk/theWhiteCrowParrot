
"""
This module contains all object representing the node the Zone category.
Thats mainly data stuctures.
"""

from corax.coordinate import to_block_position


class Zone:
    """
    Zode of the "zone" categorie. It is coordinate
    where the "affected" character are not allowed to go.
    """
    def __init__(self, data):
        self.data = data
        self.enable = data.get("enable", True)

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

    def set_rect(self, rect):
        self.data["zone"] = rect

    @property
    def relationship(self):
        return self.data["relationship"]

    @property
    def target(self):
        return self.data["target"]

    @property
    def subject(self):
        return self.data["subject"]

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
    def event(self):
        return self.data.get("event")

    @property
    def event_names(self):
        return self.data.get("events")

    @property
    def trigger(self):
        return self.data.get("trigger")

    @property
    def affect(self):
        return self.data["affect"] or []

    @property
    def hitmaps(self):
        return self.data.get("hitmaps", [])

    def __repr__(self):
        return f"Zone: {self.name}: {self.l}, {self.r}, {self.t}, {self.b}"