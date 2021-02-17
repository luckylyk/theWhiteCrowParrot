import json

import corax.context as cctx
from corax.core import NODE_TYPES
from corax.moves import filter_moves_by_inputs, filter_unholdable_moves, MovementManager
from corax.animation import SpriteSheet
from corax.coordinates import Coordinate, map_pixel_position, to_block_position, to_pixel_position
from corax.gamepad import InputBuffer
from corax.pygameutils import render_image, render_rect, render_text
from corax.mathutils import sum_num_arrays


class Player():
    def __init__(
            self,
            name,
            movement_manager,
            input_buffer,
            coordinates,
            sound_shooter=None):

        self.name = name
        self.movement_manager = movement_manager
        self.input_buffer = input_buffer
        self.coordinates = coordinates
        self.sound_shooter = sound_shooter
        self.zones = []

    @staticmethod
    def from_filename(
            filename,
            name,
            start_position,
            pixel_offset,
            flip=False,
            sound_shooter=None):

        coordinates = Coordinate(start_position, pixel_offset, flip)
        input_buffer = InputBuffer()
        spritesheet = SpriteSheet.from_filename(name, filename)
        with open(filename, 'r') as f:
            data = json.load(f)
        movement_manager = MovementManager(data, spritesheet, coordinates)
        return Player(
            name,
            movement_manager,
            input_buffer,
            coordinates,
            sound_shooter)

    def add_zone(self, zone):
        if zone.type == NODE_TYPES.NO_GO:
            self.movement_manager.no_go_zones.append(zone)
            return
        self.zones.append(zone)

    def update_inputs(self, joystick):
        flip = self.coordinates.flip
        data = self.movement_manager.data
        keystate_changed = self.input_buffer.update(joystick, flip)
        if keystate_changed is False:
            return

        moves = filter_moves_by_inputs(data, self.input_buffer)
        unholdable = filter_unholdable_moves(data, self.input_buffer)
        self.movement_manager.unhold(unholdable)
        self.movement_manager.propose_moves(moves)

    def evaluate(self):
        self.movement_manager.evaluate()
        trigger = self.movement_manager.trigger
        if trigger is not None:
            self.sound_shooter.triggers.append(trigger)

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        render_image(self.movement_manager.image, screen, position)
        if not cctx.DEBUG:
            return
        # This code should not polluate the main process and should be set
        # somewhere else, have to think about how to manage those cases.
        # Render a spot following the player animation center in debug mode
        size = self.movement_manager.data["frame_size"]
        center = self.movement_manager.animation.pixel_center
        position = sum_num_arrays(center, self.pixel_position)
        x, y = camera.relative_pixel_position(position, deph)
        render_rect(screen, (255, 255, 0), x-1, y-1, 2, 2, 255)
        position = to_block_position(position)
        position = to_pixel_position(position)
        x, y = camera.relative_pixel_position(position, deph)
        size = cctx.BLOCK_SIZE
        render_rect(screen, (150, 150, 255), x, y, size, size, 50)
        pcenter = self.movement_manager.animation.pixel_center
        bcenter = to_block_position(pcenter)
        bcenter = sum_num_arrays(self.coordinates.block_position, bcenter)
        wpcenter = sum_num_arrays(self.coordinates.pixel_position, pcenter)
        text = f"{self.name}"
        render_text(screen, (155, 255, 0), 0, 0, text)
        text = f"    (position: {self.coordinates.block_position})"
        render_text(screen, (155, 255, 0), 0, 15, text)
        text = f"    (center pixel position: {self.movement_manager.animation.pixel_center})"
        render_text(screen, (155, 255, 0), 0, 30, text)
        text = f"    (center block position: {bcenter}"
        render_text(screen, (155, 255, 0), 0, 45, text)
        text = f"    (global pixel center: {wpcenter}"
        render_text(screen, (155, 255, 0), 0, 60, text)

    @property
    def pixel_center(self):
        return sum_num_arrays(
            self.animation.pixel_center, self.coordinates.pixel_position)

    @property
    def animation(self):
        return self.movement_manager.animation

    @property
    def pixel_position(self):
        return self.coordinates.pixel_position

    @property
    def deph(self):
        return self.coordinates.deph

    @property
    def size(self):
        return self.movement_manager.image.get_size()
