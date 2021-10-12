import json

from corax.animation import SpriteSheet
from corax.controller import AnimationController
from corax.coordinate import Coordinate
from corax.pygameutils import load_image, render_image


class SetStaticElement():
    def __init__(self, name, image, pixel_position=None, deph=0):
        self.name = name
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.deph = deph
        self.visible = True

    @staticmethod
    def from_filename(filename, name, pixel_position=None, key_color=None, deph=0):
        image = load_image(filename, key_color)
        return SetStaticElement(name, image, pixel_position, deph)

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.image, screen, position)

    @property
    def size(self):
        return self.image.get_size()


class SetAnimatedElement():
    def __init__(self, name, animation_controller, coordinate, deph, alpha=255):
        self.name = name
        self.animation_controller = animation_controller
        self.coordinate = coordinate
        self.deph = deph
        self.alpha = alpha
        self.visible = True

    @staticmethod
    def from_filename(name, filename, pixel_position, deph, alpha):
        spritesheet = SpriteSheet.from_filename(None, filename)
        with open(filename, 'r') as f:
            data = json.load(f)
        coordinate = Coordinate(pixel_offset=pixel_position)
        animation_controller = AnimationController(data, spritesheet, coordinate)
        return SetAnimatedElement(
            name, animation_controller, coordinate, deph, alpha)

    @property
    def pixel_position(self):
        return self.coordinate.pixel_position

    @property
    def trigger(self):
        return self.animation_controller.trigger

    def evaluate(self):
        self.animation_controller.evaluate()

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        for image in self.animation_controller.images:
            render_image(image, screen, position, self.alpha)