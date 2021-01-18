import json


from whitecrow.animation import SpriteSheet
from whitecrow.cordinates import Cordinates
from whitecrow.pygameutils import load_image, render_image
from whitecrow.moves import MovementManager


class SetStaticElement():
    def __init__(self, image, pixel_position=None, elevation=0):
        self.name = None
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.elevation = elevation

    @staticmethod
    def from_filename(filename, pixel_position=None, key_color=None, elevation=0):
        image = load_image(filename, key_color)
        return SetStaticElement(image, pixel_position, elevation)

    def render(self, screen, position):
        render_image(self.image, screen, position)

    @property
    def size(self):
        return self.image.get_size()


class SetAnimatedElement():
    def __init__(self, movement_manager, cordinates, elevation, alpha=25):
        self.name = None
        self.movement_manager = movement_manager
        self.cordinates = cordinates
        self.elevation = elevation
        self.alpha = alpha

    @staticmethod
    def from_filename(filename, pixel_position, elevation):
        spritesheet = SpriteSheet.from_filename(filename)
        with open(filename, 'r') as f:
            datas = json.load(f)
        cordinates = Cordinates(pixel_offset=pixel_position)
        movement_manager = MovementManager(datas, spritesheet, cordinates)
        return SetAnimatedElement(movement_manager, cordinates, elevation)

    @property
    def pixel_position(self):
        return self.cordinates.pixel_position

    def next(self):
        self.movement_manager.next()

    def render(self, screen, position):
        render_image(self.movement_manager.image, screen, position, self.alpha)