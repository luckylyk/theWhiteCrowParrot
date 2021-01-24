

import random
import math
from functools import partial
from itertools import cycle


from whitecrow.mathutils import normalize, clamp, difference
from whitecrow.core import PARTICLE_SHAPE_TYPES
from whitecrow.pygameutils import render_rect, render_ellipse
from whitecrow.euclide import (
    Rect, angle_to_vector, vector_to_angle, points_to_vector, limit_angle)


DEFAULT_SPOT_OPTIONS = {
    "boundary_behavior": "kill_on_boundary",
    "speed": (1, 5),
    "frequency": (10, 15)}


DEFAULT_DIRECTION_OPTIONS = {
    "rotation_range": -.25,
    "speed": 10,
    "limits": (-math.pi, math.pi)}


def spot_out_of_boundary(kill, slow_down, spot, zone):
    if kill and slow_down:
         kill = spot.speed <=  0
    if kill is True:
        spot.is_dead = True
    if slow_down is True and spot.speed > 0:
        spot.speed -= 1
        spot.speed = max(spot.speed, 0)


SPOT_BOUNDARY_BEHAVIORS = {
    "kill_on_boundary": partial(spot_out_of_boundary, True, False),
    "stop_on_boundary": partial(spot_out_of_boundary, False, True),
    "bounce_on_boundary": partial(spot_out_of_boundary, False, False),
    "slow_and_kill_on_boundary": partial(spot_out_of_boundary, True, True)}


def chose_random_position(zone):
    x = random.randrange(zone.left, zone.right)
    y = random.randrange(zone.top, zone.bottom)
    return x, y


def build_emitter(zone, spots):
    return partial(emit_spot_position, zone=zone, spots=spots)


def emit_spot_position(field, zone=None, spots=None):
    if zone is not None:
        return chose_random_position(zone)
    if spots is not None:
        return random.choice(spots)
    return chose_random_position(field.zone)


def build_spot_options(options):
    result = DEFAULT_SPOT_OPTIONS.copy()
    result.update(options)
    return result


def build_direction_options(options):
    result = DEFAULT_DIRECTION_OPTIONS.copy()
    result.update(options)
    return result


class ParticlesSystem():
    def __init__(
            self,
            zone,
            name,
            elevation,
            start_number,
            spot_options=None,
            direction_options=None,
            shape_options=None,
            flow=0,
            emitter=None):

        self.name = name
        self.elevation = elevation
        self.zone = Rect(*zone)
        self.flow = cycle(range(flow)) if flow else None
        self.emitter = emitter
        self.spot_options = build_spot_options(spot_options or {})
        self.direction_options = build_direction_options(direction_options or {})
        self.shape_options = shape_options

        self.spots = []
        self.build_start_states(start_number)

    @property
    def pixel_position(self):
        return self.zone.top_left

    @property
    def size(self):
        return self.zone.width, self.zone.height

    def build_start_states(self, n):
        for _ in range(n):
            self.spots.append(self.build_spot())

    def build_spot(self):
        position = self.emitter(self)
        behavior = DirectionBehavior(**self.direction_options)
        return Spot(
            position=position,
            direction_behavior=behavior,
            zone=self.zone,
            **self.spot_options)

    def clear_dead_spots(self):
        to_delete = [spot for spot in self.spots if spot.is_dead]
        for spot in to_delete:
            self.spots.remove(spot)

    def next(self):
        if self.flow is not None:
            flow = next(self.flow)
            if flow == 0:
                self.spots.append(self.build_spot())
        self.clear_dead_spots()
        for spot in self.spots:
            spot.next()

    def render(self, screen, position):
        color = self.shape_options["color"]
        for spot in self.spots:
            x = position[0] + spot.pixel_position[0] - self.pixel_position[0]
            y = position[1] + spot.pixel_position[1] - self.pixel_position[1]
            size = self.shape_options["size"]
            if self.shape_options["type"] == PARTICLE_SHAPE_TYPES.SQUARE:
                render_rect(screen, color, x, y, size, size)
            elif self.shape_options["type"] == PARTICLE_SHAPE_TYPES.ELLIPSE:
                render_ellipse(screen, color, x, y, size, size)


class DirectionBehavior():
    def __init__(self, rotation_range, speed, limits):
        self.range = rotation_range
        self.speed = speed
        self.limits = limits

    def get_target(self, direction):
        offset = random.uniform(-self.range, self.range)
        return (direction or 0) + offset

    def next_direction(self, direction, target, way, limit):
        dif = difference(target, direction) / self.speed
        if -.0002 < dif < .0002:
            return direction
        direction += dif if way else -dif
        direction = normalize(direction, -math.pi, math.pi)
        if limit:
            return limit_angle(direction, self.limits[0], self.limits[1])
        return direction

    def limit(self, direction):
        return limit_angle(direction, self.limits[0], self.limits[1])


class Spot():
    def __init__(
            self,
            position,
            direction_behavior,
            boundary_behavior,
            speed,
            frequency,
            zone):

        self.position = position
        self.direction = None
        self.target = None
        self.direction_behavior = direction_behavior
        self.boundary_behavior = SPOT_BOUNDARY_BEHAVIORS[boundary_behavior]
        self.speed = random.uniform(*speed)
        frequency = random.randrange(*frequency)
        self.frequency = cycle(range(frequency))
        self.zone = zone
        self.is_dead = False
        self.way = random.choice([True, False]) # True is left, False is right

        # set a random start index
        for _ in range(random.randrange(frequency)):
            next(self.frequency)

    def next_direction_target(self):
        if not self.zone.contains(self.position):
            vector = points_to_vector(self.zone.center, self.position)
            direction = vector_to_angle(vector) or math.pi
            self.target = normalize(direction, -math.pi, math.pi)
            return
        self.way = random.choice([True, False])
        self.target = self.direction_behavior.get_target(self.direction)

    @property
    def pixel_position(self):
        return round(self.position[0]), round(self.position[1])

    def next_direction(self):
        if self.target is None:
            self.next_direction_target()
        if self.direction is None:
            self.direction = self.target
            return
        self.direction = self.direction_behavior.next_direction(
            self.direction,
            self.target,
            self.way,
            self.zone.contains(self.position))

    def next(self):
        index = next(self.frequency)
        if index == 0:
            self.next_direction_target()
        if not self.zone.contains(self.position):
            self.boundary_behavior(self, self.zone)
        self.next_direction()
        vector = angle_to_vector(self.direction)
        x = self.position[0] + (vector[0] * self.speed)
        y = self.position[1] + (vector[1] * self.speed)
        self.position = x, y
