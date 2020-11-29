

import random
import math
from functools import partial
from itertools import cycle

from whitecrow.mathutils import normalize, clamp, difference
from whitecrow.euclide import (
    Rect, angle_to_vector, vector_to_angle, points_to_vector, limit_angle)


DEFAULT_SPOT_OPTIONS = {
    "boundary_behavior": "kill_on_boundary",
    "speed": (1, 5),
    "frequency": (10, 15),}


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


class Field():
    def __init__(
            self,
            zone,
            start_number,
            spot_options=None,
            flow=0,
            emitter=None):

        self.zone = zone
        self.flow = cycle(range(flow)) if flow else None
        self.emitter = emitter
        self.spot_options = build_spot_options(spot_options or {})

        self.spots = []
        self.build_start_states(start_number)

    def build_start_states(self, n):
        for _ in range(n):
            self.spots.append(self.build_spot())

    def build_spot(self):
        position = self.emitter(self)
        behavior = DirectionBehavior(
            range_=-.25,
            speed=10,
            limits=(-math.pi, math.pi))
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


class DirectionBehavior():
    def __init__(self, range_, speed, limits):
        self.range = range_
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
        self.speed = random.randrange(*speed)
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
