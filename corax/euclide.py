"""
This is an base module providing math function related to geometry and
trigonometry and shape collisions.
"""

import math
from corax.mathutils import normalize, linear_ratio


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


def get_rect_falloff_ratio(left, top, right, bottom, position, falloff):
    """
     _______________________________
    |                               |
    |    _______________________    |<--- rect as (left, top, right, bottom)
    |   |                       |   |
    |   |                       |<--|-----falloff limit
    |   |_______________________|   |
    |                               |
    |_______________________________|

    This function compute the value of a position in a rectangle.
    Inside the falloff limit, it return 1 (the max position)
    Outside the rect it returns 0.
    In between, it compute the ratio between each. That's mainly used to drive
    the sound volume comparing the listener to the emission zone.
    """
    ratio_x = None
    ratio_y = None

    if left <= position[0] <= left + falloff:
        ratio_x = 1 - linear_ratio(position[0], left, left + falloff)
    elif right - falloff <= position[0] <= right:
        ratio_x = linear_ratio(position[0], right - falloff, right)

    if top < position[1] < top + falloff:
        ratio_y = 1 - linear_ratio(position[1], top, top + falloff)
    elif bottom - falloff < position[1] < bottom:
        ratio_y = linear_ratio(position[1], bottom - falloff, bottom)

    if ratio_x is None and ratio_y is None:
        raise ValueError(f"position {position} not in the falloff zone")
    elif ratio_y is None:
        return ratio_x
    elif ratio_x is None:
        return ratio_y
    return min([ratio_x, ratio_y])


def collision_rect_rect(r1, r2):
    if (r1.left < r2.left + r1.width and
        r1.left + r2.width > r2.left and
        r1.height < r2.height + r1.height and
        r1.height + r1.top > r2.top):
        return True
    return (
        any(r1.contains(c) for c in r2.corners) or
        any(r2.contains(c) for c in r1.corners))


class Rect():
    """
    Common class representing a rectangle.
    """
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @staticmethod
    def xywh(left, top, width, height):
        return Rect(left, top, left + width, top + height)

    @property
    def center(self):
        return (
            self.left + round(self.width / 2),
            self.top + round(self.height / 2))

    @property
    def top_left(self):
        return self.left, self.top

    @property
    def bottom_left(self):
        return self.left, self.bottom

    @property
    def top_right(self):
        return self.right, self.top

    @property
    def bottom_right(self):
        return self.right, self.bottom

    @property
    def corners(self):
        return (
            self.top_left,
            self.top_right,
            self.bottom_left,
            self.bottom_right)

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

    def inside_main_zone(self, pixel_position, falloff):
        return (
            self.left + falloff < pixel_position[0] < self.right - falloff and
            self.top + falloff < pixel_position[1] < self.bottom - falloff)

    def falloff_ratio(self, pixel_position, falloff):
        if self.contains(pixel_position) is False:
            return 0
        if self.inside_main_zone(pixel_position, falloff) is True:
            return 1
        return get_rect_falloff_ratio(
            self.left,
            self.top,
            self.right,
            self.bottom,
            pixel_position,
            falloff)

    def __repr__(self):
        return f"{self.left}, {self.top}, {self.right} ,{self.bottom}"

    def collide_rect(self, rect):
        return collision_rect_rect(self, rect)
