import json

from corax.animation import SpriteSheet
from corax.coordinates import Coordinate
from corax.pygameutils import load_image, render_image
from corax.moves import AnimationController


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
    def __init__(self, name, animation_controller, coordinates, deph, alpha=255):
        self.name = name
        self.animation_controller = animation_controller
        self.coordinates = coordinates
        self.deph = deph
        self.alpha = alpha

    @staticmethod
    def from_filename(name, filename, pixel_position, deph, alpha):
        spritesheet = SpriteSheet.from_filename(None, filename)
        with open(filename, 'r') as f:
            data = json.load(f)
        coordinates = Coordinate(pixel_offset=pixel_position)
        animation_controller = AnimationController(data, spritesheet, coordinates)
        return SetAnimatedElement(
            name, animation_controller, coordinates, deph, alpha)

    @property
    def pixel_position(self):
        return self.coordinates.pixel_position

    def evaluate(self):
        self.animation_controller.evaluate()

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.animation_controller.image, screen, position, self.alpha)