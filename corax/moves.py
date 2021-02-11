
import json
import logging
import os

import corax.context as cctx
from corax.core import EVENTS
from corax.animation import SpriteSheet, build_centers_list
from corax.cordinates import to_block_position, to_pixel_position, map_pixel_position, flip_position
from corax.mathutils import sum_num_arrays


def filter_moves(datas, input_buffer):
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
    moves = []
    for move in datas["evaluation_order"]:
        if datas["moves"][move]["hold"] is False:
            continue
        inputs = datas["moves"][move]["inputs"]
        if any(i in input_buffer.released_delta() for i in inputs):
            moves.append(move)
    return moves


def is_move_change_authorized(move, datas, animation):
    if animation.is_lock():
        return False
    move_datas = datas["moves"][move]
    conditions = move_datas["conditions"]
    if not conditions:
        return True
    return (
        animation.name in conditions.get("animation_in", []) and
        animation.name not in conditions.get("animation_not_in", []))


def is_move_cross_zone(
        datas, move, block_position, flip, zones, image_size):
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
    def __init__(self, datas, spritesheet, cordinates):
        self.cordinates = cordinates
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
        for move in moves:
            valid = is_move_change_authorized(move, self.datas, self.animation)
            if self.is_offset_allowed(move) and valid:
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
        block_position = self.cordinates.block_position
        block_offset = self.animation.post_events.get(EVENTS.BLOCK_OFFSET)
        if block_offset:
            fp = self.cordinates.flip
            block_offset = flip_position(block_offset) if fp else block_offset
            block_position = sum_num_arrays(block_position, block_offset)
        return not is_move_cross_zone(
            move=move,
            image_size=self.datas["image_size"],
            block_position=block_position,
            flip=self.cordinates.flip,
            datas=self.datas,
            zones=self.no_go_zones)

    def set_move(self, move):
        self.moves_buffer = []
        if self.animation is not None:
            for event, value in self.animation.post_events.items():
                self.apply_event(event, value)
                msg = f"EVENT: {self.animation.name}, {event}, {value}"
                logging.debug(msg)
        flip = self.cordinates.flip
        self.animation = self.spritesheet.build_animation(move, flip)
        for event, value in self.animation.pre_events.items():
            self.apply_event(event, value)
            msg = f"EVENT: {self.animation.name}, {event}, {value}"
            logging.debug(msg)

    def apply_event(self, event, value):
        if event == EVENTS.BLOCK_OFFSET:
            flip = self.cordinates.flip
            block_offset = flip_position(value) if flip else value
            self.cordinates.block_position[0] += block_offset[0]
            self.cordinates.block_position[1] += block_offset[1]
        elif event == EVENTS.FLIP:
            self.cordinates.flip = not self.cordinates.flip
        elif event == EVENTS.SWITCH_TO:
            filename = os.path.join(cctx.MOVE_FOLDER, value)
            self.spritesheet = SpriteSheet.from_filename(value, filename)
            with open(filename, 'r') as f:
                self.datas = json.load(f)

    def set_next_move(self):
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

    def next(self):
        anim = self.animation
        if anim.is_finished() and anim.hold is False:
            self.set_next_move()
        if anim.is_finished() and anim.hold is True and anim.repeatable:
            # this repeat the current animation or next animation on the loop
            if self.is_offset_allowed(self.animation.loop_on):
                self.set_move(self.animation.loop_on)
            else:
                self.animation.hold = False
        self.animation.next()
        self.cordinates.center_offset = self.animation.pixel_center

    @property
    def trigger(self):
        return self.animation.trigger

    @property
    def image(self):
        return self.animation.image

