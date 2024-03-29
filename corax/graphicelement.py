from corax.animation import SpriteSheet
from corax.controller import AnimationController
from corax.coordinate import Coordinate
from corax.mathutils import sum_num_arrays
from corax.override import load_json
from corax.renderengine.io import load_image


class SetStaticElement:
    def __init__(self, name, image, pixel_position=None, visible=True, deph=0):
        self.name = name
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.deph = deph
        self.visible = visible

    @staticmethod
    def from_filename(
            filename, name, pixel_position=None,
            key_color=None, visible=True, deph=0):
        image = load_image(filename, key_color)
        return SetStaticElement(name, image, pixel_position, visible, deph)

    @property
    def size(self):
        return self.image.get_size()


class SetAnimatedElement:
    def __init__(
            self, name, animation_controller,
            coordinate, visible, deph, alpha=255):
        self.name = name
        self.animation_controller = animation_controller
        self.coordinate = coordinate
        self.deph = deph
        self.alpha = alpha
        self.visible = visible

    @staticmethod
    def from_filename(name, filename, pixel_position, visible, deph, alpha):
        spritesheet = SpriteSheet.from_filename(None, filename)
        data = load_json(filename)
        coordinate = Coordinate(pixel_position=pixel_position)
        animation_controller = AnimationController(
            data, spritesheet, coordinate)
        return SetAnimatedElement(
            name, animation_controller, coordinate, visible, deph, alpha)

    @property
    def pixel_center(self):
        center = self.animation_controller.animation.pixel_center
        pos = [center, self.coordinate.pixel_position]
        if None in pos:
            return
        return sum_num_arrays(*pos)

    @property
    def hitmaps(self):
        return self.animation_controller.animation.hitmaps

    @property
    def pixel_position(self):
        return self.coordinate.pixel_position

    @property
    def trigger(self):
        return self.animation_controller.trigger

    def evaluate(self):
        self.animation_controller.evaluate()
