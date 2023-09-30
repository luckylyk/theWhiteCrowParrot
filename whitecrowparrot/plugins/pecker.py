"""
This Plugin is a implementation of the Pecker's behavior in the forest.
The pecker can fly around the White Crow Parrot and and react when she's throws
seeds on the ground for him.
The main stuff is when WCP is thowing the seed on the trunk on the other side
of the river. Picking the seeds, the pecker must break the tree which fall on
the right side and create a natural (unstable) bridge to cross the river.

plugin type is "pecker"

data structure example to add in a json scene is:
    {
        "name": "pecker",
        "type": "plugin",
        "file": "pecker_flying_around.json",
        "ptype": "pecker",
        "pixel_position": [2000, 125],
        "flip": false,
        "target": "whitecrow",
        "offset": [0, -130],
        "enable": false,
        "deph": 0.0
    },

Available crackle commands are:
    throw_seeds
    start_from
    reset
"""


import os
import re
import math
import corax.context as cctx
from corax.animation import SpriteSheet
from corax.iterators import cycle
from corax.pluginapi import CoraxPluginShape
from corax.seeker import find_element
from corax.mathutils import sum_num_arrays
from corax.crackle.parser import string_to_int_list

points = [
    (0, 0), (48, -1), (102, -8), (120, -25), (128, -44), (128, -75),
    (113, -90), (93, -63), (88, -30), (83, -16), (38, 28), (0, 35)]

reversed_points = list(reversed([(-p[0], p[1]) for p in points]))
HEIGHTS_PATH_CVS = points + reversed_points
BLEND_START_DURATION = 40
BLEND_THROW_DURATION = 40
THROW_OFFSET = [195, -13]
TROMPATH_CV = [
    (270, 50),
    (230, 17),
    (210, 10),
    (180, 5),
    (130, 3),
    (100, 2.5),
    (60, 2)
]


class PECKER_STATUSES:
    FLY_HOVER = 'flying_hover'
    STARTING = 'starting'
    REACH_SEEDS = 'reach_seeds'
    PICKING = 'picking'


class Pecker(CoraxPluginShape):
    ptype = 'pecker'

    def __init__(self, name, scene, data):
        super().__init__(name, scene, data)
        self.initialize()

    def initialize(self):
        self.status = PECKER_STATUSES.FLY_HOVER
        self.points = bezier_interpolation(HEIGHTS_PATH_CVS, 100)[:-1]
        self.path = None
        self.pixel_position_buffer = self.data['pixel_position'][:]
        self._pixel_position = self.data['pixel_position'][:]
        self.enable = self.data['enable']
        self._deph = self.data['deph']
        self.deph_buffer = None
        self.spritesheet = build_spritesheet(self.data)
        self.animation = None
        self.buffer_point = None
        self.path = []
        self.index_iterator = cycle(list(range(len(self.points))))
        self.buffer = []
        self.offset = self.data['offset']
        self.target = find_element(self.scene, self.data['target'])
        self.flip = True

    def evaluate(self):
        if not self.enable:
            return
        if self.deph_buffer:
            self._deph = self.deph_buffer.pop(0)
        if self.status == PECKER_STATUSES.STARTING:
            self.evaluate_fly_hover()
        if self.status == PECKER_STATUSES.FLY_HOVER:
            self.evaluate_fly_hover()
        if self.status == PECKER_STATUSES.REACH_SEEDS:
            self.evaluate_reach_seeds()
        if self.status == PECKER_STATUSES.PICKING:
            self.evaluate_animation('picking')

    def evaluate_starting(self):
        self.buffer.append(self.center)
        self.buffer = self.buffer[-20:]
        center = self.points[next(self.index_iterator)]
        x1 = self.buffer_point[0] / self.blend_start_transit
        x2 = center[0] / (BLEND_START_DURATION - self.blend_start_transit)
        y1 = self.buffer_point[1] / self.blend_start_transit
        y2 = center[1] / (BLEND_START_DURATION - self.blend_start_transit)
        self._pixel_position = [x1 + x2, y1 + y2]
        self.blend_start_transit -= 1
        if self.blend_start_transit == 0:
            self.status = PECKER_STATUSES.FLY_HOVER

    def evaluate_reach_seeds(self):
        if distance_2d(self._pixel_position, self.buffer_point) < 2:
            return self.start_picking()
        if self.path:
            x, y = self.path.pop(0)
        else:
            x, y = self.buffer[-1]
        self.buffer.append([x, y])
        self.buffer = self.buffer[-20:]
        x = sum(p[0] for p in self.buffer) / len(self.buffer)
        y = sum(p[1] for p in self.buffer) / len(self.buffer)
        if self.blend_start_transit:
            div = (self.blend_start_transit / 35)
            x += int(self.points[self.index_iterator.value][0] * div)
            y += int(self.points[self.index_iterator.value][1] * div)
            self.blend_start_transit -= 1
        self._pixel_position = [x, y]
        self.flip = self.pixel_position_buffer[0] < self._pixel_position[0]
        self.pixel_position_buffer = self._pixel_position[:]
        self.evaluate_animation('fly_hover')

    def evaluate_fly_hover(self):
        self.buffer.append(self.center)
        self.buffer = self.buffer[-20:]
        x = sum(p[0] for p in self.buffer) / len(self.buffer)
        y = sum(p[1] for p in self.buffer) / len(self.buffer)
        index = next(self.index_iterator)
        self._pixel_position = [
            (self.points[index][0] + x), (self.points[index][1] + y)]
        self.flip = self.pixel_position_buffer[0] < self._pixel_position[0]
        self.pixel_position_buffer = self._pixel_position[:]
        self.evaluate_animation('fly_hover')

    def evaluate_animation(self, next_move):
        if not self.animation or self.animation.is_finished():
            layers = list(self.spritesheet.sequences)
            self.animation = self.spritesheet.build_animation(
                next_move, self.flip, layers)
            return
        self.animation.next()

    def start_picking(self):
        self.status = PECKER_STATUSES.PICKING
        layers = list(self.spritesheet.sequences)
        self.animation = self.spritesheet.build_animation(
            "picking", self.flip, layers)

    @property
    def center(self):
        if not self.animation:
            return sum_num_arrays(
                self.offset, self.target.coordinate.pixel_center)
        offsetx = self.animation.pixel_center[0]
        offsety = self.animation.pixel_center[1]
        center = [
            self.target.coordinate.pixel_center[0] - offsetx,
            self.target.coordinate.pixel_center[1] - offsety]
        return sum_num_arrays(self.offset, center)

    @property
    def pixel_position(self):
        return self._pixel_position

    @property
    def visible(self):
        return self.enable

    @property
    def deph(self):
        return self._deph

    @property
    def images(self):
        return self.animation.images

    def render_debug(self, surface, layer_deph, camera):
        from corax.renderengine.draw import draw_ellipse
        deph = self.deph + layer_deph
        if self.buffer_point:
            p = camera.relative_pixel_position(self.buffer_point, deph)
            draw_ellipse(surface, 'yellow', p[0], p[1], 5, 5, True)
        p = camera.relative_pixel_position(self.center, deph)
        draw_ellipse(surface, 'purple', p[0], p[1], 5, 5, True)
        draw_ellipse(surface, 'purple', p[0], p[1], 5, 5, True)
        p = camera.relative_pixel_position(self.pixel_position, deph)
        draw_ellipse(surface, 'black', p[0], p[1], 5, 5, True)
        if self.buffer:
            for p in self.buffer:
                p = camera.relative_pixel_position(p, deph)
                draw_ellipse(surface, 'orange', p[0], p[1], 3, 3, True)
        if self.path:
            for p in self.path:
                p = camera.relative_pixel_position(p, deph)
                draw_ellipse(surface, 'red', p[0], p[1], 3, 3, True)
            for p in self.cv:
                p = camera.relative_pixel_position(p, deph)
                draw_ellipse(surface, 'blue', p[0], p[1], 5, 5, True)

    def throw_seeds(self, position=None):
        if position is None:
            offset = THROW_OFFSET[:]
            if self.target.coordinate.flip:
                offset[0] = -offset[0]
            self.buffer_point = sum_num_arrays(
                self.target.coordinate.pixel_center, offset)
        else:
            self.buffer_point = position
        self.status = PECKER_STATUSES.REACH_SEEDS
        self.blend_start_transit = BLEND_THROW_DURATION
        self.path, self.cv = get_throw_path(
            self.center, self.buffer_point)

    def startfrom(self, position, deph):
        self.status = PECKER_STATUSES.STARTING
        self.enable = True
        self.blend_start_transit = BLEND_START_DURATION
        self._pixel_position = position
        self.buffer_point = position
        self.buffer = [position]
        self._deph = deph
        self.deph_buffer = linear_interpolation(
            deph, self.data['deph'], BLEND_START_DURATION)

    def collect_value(self, command):
        if command == "invisible":
            return not self.visible
        if command == "visible":
            return self.visible
        raise NotImplementedError(
            command,
            f'command is not known for plugin {self.ptype} as '
            'value collector.')

    def execute_command(self, command):
        if command == "throw_seeds":
            self.throw_seeds()
            return 0
        if command == "reset":
            self.initialize()
            return 0
        if command.split(" ")[0] == "thow_seeds_to":
            position = string_to_int_list(command.split(" ")[1])
            self.throw_seeds()
            return 0
        if command.split(" ")[0] == "startfrom":
            pattern = r'\((.*?)\)'
            position = string_to_int_list(re.findall(pattern, command)[0])
            deph = float(command.split(" ")[-1])
            self.startfrom(position, deph)
            return 0
        raise NotImplementedError(
            command, f'command is not known for plugin {self.ptype}')


def build_spritesheet(data):
    filename = data["file"]
    data_path = os.path.join(cctx.SHEET_FOLDER, filename)
    return SpriteSheet.from_filename(filename, data_path)


def bezier_interpolation(control_points, output_point_number):
    step = 1.0 / (output_point_number - 1)
    output_points = []

    for t in range(output_point_number):
        t_value = t * step
        one_minus_t = 1.0 - t_value
        points = control_points[:]

        while len(points) > 1:
            next_points = []
            for i in range(len(points) - 1):
                x = points[i][0] * one_minus_t + points[i + 1][0] * t_value
                y = points[i][1] * one_minus_t + points[i + 1][1] * t_value
                next_points.append((x, y))
            points = next_points
        output_points.append(points[0])
    return output_points


def distance_2d(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    return math.degrees(angle)


def get_vector(degree, length):
    radian = math.radians(degree)
    x = length * math.cos(radian)
    y = length * math.sin(radian)
    return x, y


def get_throw_path(start_point, end_point):
    iterations = int(distance_2d(start_point, end_point) / 7)
    original_distance = distance_2d(start_point, end_point)
    original_angle = get_angle(start_point, end_point)
    points = [start_point]
    reverse = start_point[0] < end_point[0]
    cvs = [start_point]
    for angle, division in TROMPATH_CV:
        oangle = original_angle - angle if reverse else original_angle + angle
        offset = get_vector(
            oangle, (original_distance / division) if division else 0)
        cvs.append(sum_num_arrays(start_point, offset))
    cvs.append(end_point)
    points = bezier_interpolation(cvs, iterations)
    return points, cvs


def linear_interpolation(start_value, end_value, iterations):
    """
    This function create a list of values with linear interpolation.
    """
    if iterations < 3:
        return start_value, end_value
    iterations -= 2
    difference = float(abs(end_value - start_value))
    iteration_value = difference / (iterations + 1)
    if start_value > end_value:
        iteration_value = -iteration_value
    return [start_value + (i * iteration_value) for i in range(iterations + 2)]
