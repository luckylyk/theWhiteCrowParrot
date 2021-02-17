
import math
import corax.context as cctx
from corax.mathutils import clamp
from corax.euclide import Rect


class Camera():
    """
    This class represent the scene camera. It define framing rendered. The
    offset necessary for the renders are evaluated from this class. Each
    renderable object has to request camera his position on screen through the
    method Camera.relative_pixel_position(pixel_position, deph).
    Note that the pixel_position given correspond to the top left position, not
    the center. The center can be set through the set_center method.
    """
    def __init__(self, pixel_position=None):
        self.pixel_position = pixel_position or [0, 0]

    @property
    def pixel_center(self):
        return [
            self.pixel_position[0] + cctx.RESOLUTION[0] / 2,
            self.pixel_position[1] + cctx.RESOLUTION[1] / 2]

    def set_center(self, pixel_position):
        self.pixel_position = [
            pixel_position[0] - cctx.RESOLUTION[0] / 2,
            pixel_position[1] - cctx.RESOLUTION[1] / 2]

    def relative_pixel_position(self, pixel_position, deph=0):
        offset_x = math.ceil((pixel_position[0] - self.pixel_position[0]))
        offset_y = math.ceil((pixel_position[1] - self.pixel_position[1]))
        return [offset_x + (offset_x * deph), offset_y]

    @property
    def zone(self):
        return Rect.xywh(
            self.pixel_position[0], self.pixel_position[1],
            cctx.RESOLUTION[0], cctx.RESOLUTION[1])


class Scrolling():
    """
    This object is the algorithm who move constrain the camera to a target and
    evaluate his position into the world space. The scrolling has to update the
    camera position at each frames though the Scrolling.evaluate() method.
    """
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
        # those magic numbers have to be moved onto the game data
        self.smooth_level = 1
        self.smooth_divisor = 10
        self.max_speed = 70
        self.current_area = None

    def evaluate(self):
        if self.target is None:
            return

        target_offset = self.target_offset[0]
        if self.target.flip is True:
            target_offset = -target_offset
        # define the target X that the scrolling will aim based
        tx = self.target.pixel_center[0] + target_offset

        # limit the target to the border of the scene defined by hard boundary
        left = self.hard_boundary.left + (cctx.RESOLUTION[0] / 2)
        right = self.hard_boundary.right - (cctx.RESOLUTION[0] / 2)
        tx = clamp(tx, left, right)

        # limit the target to the current soft boundary if there is
        for area in self.soft_boundaries:
            if area.contains(self.target.pixel_center):
                aleft = area.left + (cctx.RESOLUTION[0] / 2)
                aright = area.right - (cctx.RESOLUTION[0] / 2)
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
