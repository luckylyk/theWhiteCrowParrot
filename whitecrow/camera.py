
import math
from whitecrow.mathutils import clamp
from whitecrow.prefs import PREFS
from whitecrow.euclide import Rect


def get_render_zone():
    return Rect(0, 0, PREFS["resolution"][0], PREFS["resolution"][1])


class Camera():
    def __init__(self, pixel_position=None):
        self.pixel_position = pixel_position or [0, 0]

    @property
    def pixel_center(self):
        return [
            self.pixel_position[0] + PREFS["resolution"][0] / 2,
            self.pixel_position[1] + PREFS["resolution"][1] / 2]

    def set_center(self, pixel_position):
        self.pixel_position = [
            pixel_position[0] - PREFS["resolution"][0] / 2,
            pixel_position[1] - PREFS["resolution"][1] / 2]

    def relative_pixel_position(self, pixel_position, elevation=0):
        offset_x = math.ceil((pixel_position[0] - self.pixel_position[0]))
        offset_y = math.ceil((pixel_position[1] - self.pixel_position[1]))
        return [offset_x + (offset_x * elevation), offset_y]

    @property
    def zone(self):
        return Rect.xywh(
            self.pixel_position[0], self.pixel_position[1],
            PREFS["resolution"][0], PREFS["resolution"][1])


class Scrolling():
    def __init__(
            self,
            camera,
            hard_boundary,
            target=None,
            soft_boundaries=None,
            target_offset=None):

        self.target = target
        self.camera = camera
        self.hard_boundary = hard_boundary
        self.soft_boundaries = soft_boundaries or []
        self.target_offset = target_offset or [0, 0]
        self.buffer_x = []
        self.smooth_level = 1
        self.smooth_divisor = 10
        self.max_speed = 35
        self.current_area = None

    def next(self):
        if self.target is None:
            return

        target_offset = self.target_offset[0]
        if self.target.mirror is True:
            target_offset = -target_offset
        # define the target X that the scrolling will aim based
        tx = self.target.pixel_center[0] + target_offset

        # limit the target to the border of the scene defined by hard boundary
        left = self.hard_boundary.left + (PREFS["resolution"][0] / 2)
        right = self.hard_boundary.right - (PREFS["resolution"][0] / 2)
        tx = clamp(tx, left, right)

        # limit the target to the current soft boundary if there is
        for area in self.soft_boundaries:
            if area.contains(self.target.pixel_center):
                aleft = area.left + (PREFS["resolution"][0] / 2)
                aright = area.right - (PREFS["resolution"][0] / 2)
                tx = clamp(tx, aleft, aright)
                break

        difference_cam_target = self.camera.pixel_center[0] - tx
        # do not move the camera if the camera is close enough to target
        if abs(round(difference_cam_target)) <= 5:
            if self.buffer_x:
                self.buffer_x = []
            return

        offset = difference_cam_target / self.smooth_divisor
        # to avoid arch camera acceleration, the speed is defined but on
        # average of last speed recorded. That buffer lenght is defined by the
        # smooth level
        self.buffer_x = [offset] + self.buffer_x[:self.smooth_level]
        offset = (sum(self.buffer_x) / len(self.buffer_x))
        # limit the camera speed to avoid too arch movements
        offset = clamp(offset, -self.max_speed, self.max_speed)
        result = (clamp(self.camera.pixel_center[0] - offset, left, right))
        self.camera.set_center([result, self.camera.pixel_center[1]])
