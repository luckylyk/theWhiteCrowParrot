
from whitecrow.loaders import load_image


class StaticElement():
    def __init__(self, image, pixel_position=None, elevation=0):
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.elevation = elevation

    @staticmethod
    def from_filename(filename, pixel_position=None, key_color=None, elevation=0):
        image = load_image(filename, key_color)
        return StaticElement(image, pixel_position, elevation)
