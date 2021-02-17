
import json
import logging
import os

import corax.context as cctx
from corax.core import EVENTS
from corax.animation import SpriteSheet, build_centers_list
from corax.coordinates import to_block_position, to_pixel_position, map_pixel_position, flip_position
from corax.mathutils import sum_num_arrays


def filter_moves_by_inputs(datas, input_buffer):
    """
    Filter existing moves in spritesheet datas comparing the inputs they
    requires to the given input buffer statues.
    """
    moves = []
    for move in datas["evaluation_order"]:
        inputs = datas["moves"][move]["inputs"]
        conditions = (
            any(i in input_buffer.pressed_delta() for i in inputs) and
            all(i in input_buffer.inputs() for i in inputs))
        if conditions:
            moves.append(move)
    return moves


def filter_unholdable_moves(datas, input_buffer):
    """
    Filter existing moves in spritesheet datas comparing the inputs they and
    holdable and check if the input required to unhold them fit with the input
    buffer status.
    """
    moves = []
    for move in datas["evaluation_order"]:
        if datas["moves"][move]["hold"] is False:
            continue
        inputs = datas["moves"][move]["inputs"]
        if any(i in input_buffer.released_delta() for i in inputs):
            moves.append(move)
    return moves


def is_sequence_valid(move, datas, animation):
    """
    Check if the move given is authorized look the move conditions.
    """
    move_datas = datas["moves"][move]
    conditions = move_datas["conditions"]
    if not conditions:
        return True
    return (
        animation.name in conditions.get("animation_in", []) and
        animation.name not in conditions.get("animation_not_in", []))


def is_move_cross_zone(
        datas, move, block_position, flip, zones, image_size):
    """
    Check if the block positions centers are passing across a zone give.
    Its also checking the next animations if the given one is in the middle of
    a sequence.
    """
    move_datas = datas["moves"][move]
    block_positions = []
    while True:
        pre_offset = move_datas["pre_events"].get(EVENTS.BLOCK_OFFSET)
        post_offset = move_datas["post_events"].get(EVENTS.BLOCK_OFFSET)
        flip_event = move_datas["post_events"].get(EVENTS.FLIP)
        flip_event = flip_event or move_datas["pre_events"].get(EVENTS.FLIP)
        if (not pre_offset and not post_offset) or flip_event:
            # We assume if the first move contains a FLIP event, it will not
            # move in space (even if an offset to compensate the flip is set).
            # By the way, a case where this need to evaluate could happend in
            # the futur but this is a tricky case. The that will not be
            # implemented as far as it is not necessary.
            break
        centers = build_centers_list(move_datas, image_size, flip)
        block_positions.extend(predict_block_positions(
            centers=centers,
            image_size=image_size,
            block_position=block_position,
            flip=flip,
            pre_offset=pre_offset,
            post_offset=post_offset))

        if pre_offset:
            pre_offset = flip_position(pre_offset) if flip else pre_offset
            block_position = sum_num_arrays(block_position, pre_offset)
        if post_offset:
            post_offset = flip_position(post_offset) if flip else post_offset
            block_position = sum_num_arrays(block_position, post_offset)

        move_datas = datas["moves"][move_datas["next_move"]]

    return any(z.contains(pos) for z in zones for pos in block_positions)


def predict_block_positions(
        centers,
        image_size,
        block_position,
        flip,
        pre_offset=None,
        post_offset=None):

    if pre_offset:
        pre_offset = flip_position(pre_offset) if flip else pre_offset
        block_position = sum_num_arrays(pre_offset, block_position)

    block_positions = []
    pixel_position = to_pixel_position(block_position)

    for center in centers or []:
        center = sum_num_arrays(center, pixel_position)
        if center == pixel_position:
            continue
        block_positions.append(to_block_position(center))

    if post_offset is not None:
        pixel_offset = to_pixel_position(post_offset)
        pixel_offset = flip_position(pixel_offset) if flip else pixel_offset
        center = sum_num_arrays(pixel_offset, centers[0], pixel_position)
        block_position = to_block_position(center)
        block_positions.append(block_position)
    return block_positions


class MovementManager():
    """
    The movement manager (this name sucks, I have to find a better one) is an
    object with manage the animations sequences and how they chains. It verify
    what are the next animation possible using the conditions filters,
    the movement predictions (to manage the environment boundaries),
    check the gamepad input, animation states (on hold, repeatable,
    cancelable, etc ...).
    The datas comes from the JSON set in the <root>/moves folder. It is
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
    - moves: move datas by move name. For more details on frame datas
    dictionnary structure see the class corax.animation.Animation.
    """
    def __init__(self, datas, spritesheet, coordinates):
        self.coordinates = coordinates
        self.datas = datas
        self.animation = None
        self.no_go_zones = []
        self.spritesheet = spritesheet
        self.moves_buffer = []
        self.set_move(datas["default_move"])

    def unhold(self, unholdable):
        if self.animation.hold is False:
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
        for move in moves:
            conditions = (
                not self.animation.is_lock() and
                is_sequence_valid(move, self.datas, self.animation) and
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
        block_position = self.coordinates.block_position
        block_offset = self.animation.post_events.get(EVENTS.BLOCK_OFFSET)
        if block_offset:
            fp = self.coordinates.flip
            block_offset = flip_position(block_offset) if fp else block_offset
            block_position = sum_num_arrays(block_position, block_offset)
        return not is_move_cross_zone(
            move=move,
            image_size=self.datas["frame_size"],
            block_position=block_position,
            flip=self.coordinates.flip,
            datas=self.datas,
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
                msg = f"EVENT: {self.animation.name}, {event}, {value}"
                logging.debug(msg)
        flip = self.coordinates.flip
        self.animation = self.spritesheet.build_animation(move, flip)
        for event, value in self.animation.pre_events.items():
            self.apply_event(event, value)
            msg = f"EVENT: {self.animation.name}, {event}, {value}"
            logging.debug(msg)

    def apply_event(self, event, value):
        if event == EVENTS.BLOCK_OFFSET:
            flip = self.coordinates.flip
            block_offset = flip_position(value) if flip else value
            self.coordinates.block_position[0] += block_offset[0]
            self.coordinates.block_position[1] += block_offset[1]
        elif event == EVENTS.FLIP:
            self.coordinates.flip = not self.coordinates.flip
        elif event == EVENTS.SWITCH_TO:
            filename = os.path.join(cctx.MOVE_FOLDER, value)
            self.spritesheet = SpriteSheet.from_filename(value, filename)
            with open(filename, 'r') as f:
                self.datas = json.load(f)

    def set_next_move(self):
        """
        This method is triggered when the current animation is done. This
        algorithme is looking in the buffer to find a valid sequence. If
        nothing is found, it does set the default animation next move.
        """
        next_move = self.datas["moves"][self.animation.name]["next_move"]
        if not self.moves_buffer:
            self.set_move(next_move)
            return

        key = "animation_in"
        for move in self.moves_buffer:
            moves_filter = self.datas["moves"][move]["conditions"].get(key)
            conditions = (
                moves_filter is not None and
                self.animation.name not in moves_filter and
                next_move not in moves_filter)
            if conditions or not self.is_offset_allowed(move):
                continue
            self.set_move(move)
            return
        self.set_move(next_move)

    def evaluate(self):
        anim = self.animation
        if anim.is_finished() and anim.hold is False:
            self.set_next_move()
        if anim.is_finished() and anim.hold is True and anim.repeatable:
            # this repeat the current animation or next animation on the loop
            if self.is_offset_allowed(self.animation.loop_on):
                self.set_move(self.animation.loop_on)
            else:
                self.animation.hold = False
        self.animation.evaluate()
        self.coordinates.center_offset = self.animation.pixel_center

    @property
    def trigger(self):
        return self.animation.trigger

    @property
    def image(self):
        return self.animation.image

