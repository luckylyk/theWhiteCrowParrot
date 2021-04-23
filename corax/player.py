import json
import logging

import corax.context as cctx
from corax.core import NODE_TYPES
from corax.moves import filter_moves_by_inputs, filter_unholdable_moves
from corax.pygameutils import render_image
from corax.mathutils import sum_num_arrays


class Player():
    def __init__(
            self,
            name,
            animation_controller,
            input_buffer,
            coordinates,
            sound_shooter=None):

        self.name = name
        self.animation_controller = animation_controller
        self.input_buffer = input_buffer
        self.coordinates = coordinates
        self.sound_shooter = sound_shooter

    def add_zone(self, zone):
        if zone.type == NODE_TYPES.NO_GO:
            self.animation_controller.no_go_zones.append(zone)
            return

    def input_updated(self):
        data = self.animation_controller.data
        moves = filter_moves_by_inputs(data, self.input_buffer, self.flip)
        unholdable = filter_unholdable_moves(data, self.input_buffer, self.flip)
        self.animation_controller.unhold(unholdable)
        self.animation_controller.propose_moves(moves)
        if cctx.DEBUG:
            logging.debug(f"Proposed moves: {moves}")

    def evaluate(self):
        self.animation_controller.evaluate()
        trigger = self.animation_controller.trigger
        if trigger is not None:
            self.sound_shooter.triggers.append(trigger)

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.animation_controller.image, screen, position)

    @property
    def pixel_center(self):
        if None in [self.animation.pixel_center, self.coordinates.pixel_position]:
            return
        return sum_num_arrays(
            self.animation.pixel_center, self.coordinates.pixel_position)

    @property
    def animation(self):
        return self.animation_controller.animation

    @property
    def pixel_position(self):
        return self.coordinates.pixel_position

    @property
    def deph(self):
        return self.coordinates.deph

    @property
    def size(self):
        return self.animation_controller.image.get_size()

    @property
    def flip(self):
        return self.coordinates.flip
