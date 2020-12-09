
from whitecrow.loaders import load_image


class StaticElement():
    def __init__(self, image, pixel_position=None, elevation=0):
        self.name = None
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.elevation = elevation

    @staticmethod
    def from_filename(filename, pixel_position=None, key_color=None, elevation=0):
        image = load_image(filename, key_color)
        return StaticElement(image, pixel_position, elevation)

    def render(self, screen, position):
        screen.blit(self.image, position)

    @property
    def size(self):
        return self.image.get_size()


class AnimatedElement():
    def __init__(self, images, pixel_position, elevation, options):
        self.images = images
        self.pixel_position = pixel_position
        self.elevation = elevation
        self.options = options
        self.name = None

    def render(self, screen, position):
        screen.blit(self.image, position)