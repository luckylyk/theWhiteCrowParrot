
from whitecrow.graphicutils import load_image


class StaticElement():
    def __init__(self, image, pixel_position=None, elevation=0):
        self.pixel_position = pixel_position or [0, 0]
        self.image = image
        self.elevation = elevation

    @staticmethod
    def from_filepath(file_path, pixel_position=None, key_color=None, elevation=0):
        image = load_image(file_path, key_color)
        return StaticElement(image, pixel_position, elevation)
