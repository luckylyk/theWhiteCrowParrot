
import logging
import os

import corax.context as cctx
from corax.animation import SpriteSheet
from corax.coordinate import flip_position
from corax.core import EVENTS
from corax.mathutils import sum_num_arrays
from corax.override import load_json
from corax.sequence import (
    is_moves_sequence_valid, is_layers_authorized, is_move_cross_zone)


class AnimationController():
    """
    The animation controller (this name sucks, I have to find a better one) is an
    object with manage the animations sequences and how they chains. It verify
    what are the next animation possible using the conditions filters,
    the movement predictions (to manage the environment boundaries),
    check the gamepad input, animation states (on hold, repeatable,
    cancelable, etc ...).
    The data comes from the JSON set in the <root>/moves folder. It is
    the most convoluted data struct currently in the corax engine. They are
    represented as dictionnary:
    {
        "filename": str,
        "key_color": [int, int, int],
        "frame_size": [int, int],
        "default_move": str,
        "evaluation_order": [str, ...]
        "moves": {
            "walk_a": {},
            "walk_b": {},
            "return": {},
            "idle": {},
            ...
        }
    }
    - filename: the spriteshit filename/path, relative to <root>/animation
    - key_color: the transparency color as 8b rgb()
    - frame_size: size of an unique frame (different than the PNG filesize).
    - default_move: name of the move set by default.
    - evaluation_order: list which must contains all the name of the moves
    availables. This order is use to indicate the priority if two animation are
    valide.
    - moves: move data by move name. For more details on frame data
    dictionnary structure see the class corax.animation.Animation.
    """
    def __init__(self, data, spritesheet, coordinate, layers=None):
        self.animation = None
        self.coordinate = coordinate
        self.data = data
        self.no_go_zones = []
        self.layers = layers or [
            str(key) for key in spritesheet.data["layers"].keys()]
        self.moves_buffer = []
        self.sequence = []
        self.spritesheet = spritesheet
        self.set_move(data["default_move"])

    def unhold(self, unholdable):
        if not self.animation or self.animation.hold is False:
            return
        self.animation.hold = self.animation.name not in unholdable

    def propose_moves(self, moves):
        """
        Method to softly change animation. This method is the one used
        externally to propose an animation. If the animation isn't locked and
        the sequence is valid, it will start directly the animation. If it
        is a valid sequence but the animation is currently locked but
        bufferable, the move change request will be stored in the move buffer
        to be automatically runned when the current anime is finished.
        Note that the buffer is parsed when the current animation is ended, not
        when it is unlocked.
        """
        if not self.animation:
            return
        for move in moves:
            conditions = (
                not self.animation.is_lock() and
                is_moves_sequence_valid(move, self.data, self.animation) and
                is_layers_authorized(move, self.data, self.layers) and
                move in self.spritesheet.available_animations and
                self.is_offset_allowed(move))
            if conditions:
                self.set_move(move)
                return
            conditions = (
                self.animation.bufferable and
                move not in self.moves_buffer and
                self.animation.name != move and
                self.animation.loop_on != move)
            if conditions:
                self.moves_buffer.insert(0, move)

    def is_offset_allowed(self, move):
        """
        Check is the proposed animation or the sequence will cross a zone given
        in his internal attribute: self.zones
        """
        if not self.animation:
            return False
        block_position = self.coordinate.block_position
        block_offset = self.animation.post_events.get(EVENTS.BLOCK_OFFSET)
        flip_event = self.animation.post_events.get(EVENTS.FLIP)
        flip = not self.coordinate.flip if flip_event else self.coordinate.flip
        if block_offset:
            block_offset = flip_position(block_offset) if flip else block_offset
            block_position = sum_num_arrays(block_position, block_offset)
        return not is_move_cross_zone(
            move=move,
            image_size=self.data["frame_size"],
            block_position=block_position,
            flip=flip,
            data=self.data,
            zones=self.no_go_zones)

    def set_move(self, move):
        """
        Set a move and apply the animation pre and post event. This method is
        brute force, no check are done then, the providen move have to be
        validated before.
        """
        self.moves_buffer = []
        if self.animation is not None:
            for event, value in self.animation.post_events.items():
                self.apply_event(event, value)
                msg = f"Event: {self.animation.name}, {event}, {value}"
                logging.debug(msg)

        flip = self.coordinate.flip
        layers = self.layers
        self.animation = self.spritesheet.build_animation(move, flip, layers)
        for event, value in self.animation.pre_events.items():
            self.apply_event(event, value)
            msg = f"Event: {self.animation.name}, {event}, {value}"
            logging.debug(msg)

    def flush(self):
        """
        This method immediatly reset animation state setting back the default
        move skipping the animation post event trigger. It usually triggered
        at scene change.
        """
        flip = self.coordinate.flip
        layers = self.layers
        move = self.data["default_move"]
        self.moves_buffer = []
        self.animation = self.spritesheet.build_animation(move, flip, layers)
        logging.debug(f"Flush: {move}")

    def apply_event(self, event, value):
        if event == EVENTS.BLOCK_OFFSET:
            flip = self.coordinate.flip
            block_offset = flip_position(value) if flip else value
            self.coordinate.block_position[0] += block_offset[0]
            self.coordinate.block_position[1] += block_offset[1]
        elif event == EVENTS.FLIP:
            self.coordinate.flip = not self.coordinate.flip
        elif event == EVENTS.SWITCH_TO:
            self.set_sheet(value)

    def set_sheet(self, filename, layers=None):
        self.layers = layers or self.layers
        filepath = os.path.join(cctx.SHEET_FOLDER, filename)
        self.spritesheet = SpriteSheet.from_filename(filename, filepath)
        self.data = load_json(filepath)

    def set_next_move(self):
        """
        This method is triggered when the current animation is done. This
        algorithme is looking in the buffer to find a valid sequence. If
        nothing is found, it does set the default animation next move.
        """
        if not self.animation:
            return

        if self.sequence:
            self.set_move(self.sequence.pop(0))
            # Loop animation sequences rely on hold attribute, force unhold
            # avoid this loop to happen and force the given sequence.
            self.animation.hold = False
            return

        next_move = self.animation.next_move
        if not self.moves_buffer:
            self.set_move(next_move)
            return

        for move in self.moves_buffer:
            conditions = (
                is_moves_sequence_valid(move, self.data, self.animation) and
                is_layers_authorized(move, self.data, self.layers) and
                self.is_offset_allowed(move))
            if not conditions:
                continue
            self.set_move(move)
            return

        self.set_move(next_move)

    def evaluate(self):
        if not self.animation:
            return

        anim = self.animation
        if anim.is_finished() and anim.hold is False:
            self.set_next_move()
        if anim.is_finished() and anim.hold is True and anim.repeatable:
            if self.sequence:
                self.set_next_move()
            # this repeat the current animation or next animation on the loop
            if self.is_offset_allowed(self.animation.loop_on):
                self.set_move(self.animation.loop_on)
            else:
                self.animation.hold = False
        self.animation.evaluate()
        self.coordinate.center_offset = self.animation.pixel_center

    @property
    def trigger(self):
        if self.animation:
            return self.animation.trigger

    @property
    def images(self):
        if self.animation:
            return self.animation.images

