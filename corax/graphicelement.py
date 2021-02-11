import json

from corax.animation import SpriteSheet
from corax.cordinates import Cordinates
from corax.pygameutils import load_image, render_image
from corax.moves import MovementManager


class SetStaticElement():
    def __init__(self, image, pixel_position=None, deph=0):
        self.name = None
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.deph = deph

    @staticmethod
    def from_filename(filename, pixel_position=None, key_color=None, deph=0):
        image = load_image(filename, key_color)
        return SetStaticElement(image, pixel_position, deph)

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.image, screen, position)

    @property
    def size(self):
        return self.image.get_size()


class SetAnimatedElement():
    def __init__(self, movement_manager, cordinates, deph, alpha=25):
        self.name = None
        self.movement_manager = movement_manager
        self.cordinates = cordinates
        self.deph = deph
        self.alpha = alpha

    @staticmethod
    def from_filename(filename, pixel_position, deph):
        spritesheet = SpriteSheet.from_filename(None, filename)
        with open(filename, 'r') as f:
            datas = json.load(f)
        cordinates = Cordinates(pixel_offset=pixel_position)
        movement_manager = MovementManager(datas, spritesheet, cordinates)
        return SetAnimatedElement(movement_manager, cordinates, deph)

    @property
    def pixel_position(self):
        return self.cordinates.pixel_position

    def next(self):
        self.movement_manager.next()

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.movement_manager.image, screen, position, self.alpha)