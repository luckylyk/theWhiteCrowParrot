
# def collision_rect_rect(r1, r2):
#     if (r1.left < r2.left + r1.width and
#         r1.left + r2.width > r2.left and
#         r1.height < r2.height + r1.height and
#         r1.height + r1.top > r2.top):
#         return True
#     return (
#         any(r1.contains(c) for c in r2.corners) or
#         any(r2.contains(c) for c in r1.corners))


def collision_rect_rect(r1, r2):
    return (
        r1.right >= r2.left and
        r1.left <= r2.right and
        r1.bottom >= r2.top and
        r1.top <= r2.bottom)

# def rectRect(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h):


#     # are the sides of one rectangle touching the other?

#     return r1x + r1w >= r2x and \   # r1 right edge past r2 left
#         r1x <= r2x + r2w and \  # r1 left edge past r2 right
#         r1y + r1h >= r2y and \   # r1 top edge past r2 bottom
#         r1y <= r2y + r2h    # r1 bottom edge past r2 top




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

    def __repr__(self):
        return f"Rect: {self.left}, {self.top}, {self.right} ,{self.bottom}"

    def collide_rect(self, rect):
        return collision_rect_rect(self, rect)


if __name__ == "__main__":
    rect1 = Rect(144, 2, 170, 30)
    rect2 = Rect(128, 17, 129, 18)
    assert not collision_rect_rect(rect1, rect2)

    rect1 = Rect(144, 2, 170, 30)
    rect2 = Rect(139, 0, 150, 15)
    assert collision_rect_rect(rect1, rect2)

    rect1 = Rect(0, 0, 150, 150)
    rect2 = Rect(15, 15, 120, 120)
    assert collision_rect_rect(rect1, rect2)