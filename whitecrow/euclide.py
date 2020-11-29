import math
from whitecrow.mathutils import normalize


def angle_to_vector(angle):
    x = math.sin(angle)
    y = math.cos(angle)
    return x, y


def limit_angle(value, in_angle, out_angle):
    if in_angle < out_angle:
        return normalize(value, in_angle, out_angle)
    return normalize(value, out_angle, in_angle) + math.pi


def points_to_vector(point1, point2):
    return (point1[0] - point2[0], point1[1] - point2[1])


def vector_to_angle(vector):
    return math.atan2(vector[0], vector[1])


class Rect():
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def center(self):
        return (
            self.left + round(self.width / 2),
            self.top + round(self.height / 2))

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def contains(self, pixel_position):
        return (
            self.left < pixel_position[0] < self.right and
            self.top < pixel_position[1] < self.bottom)