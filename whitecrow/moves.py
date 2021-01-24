
import json
import os

import whitecrow.context as wctx
from whitecrow.core import EVENTS
from whitecrow.animation import SpriteSheet


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


class MovementManager():
    def __init__(self, datas, spritesheet, cordinates):
        self.cordinates = cordinates
        self.datas = datas
        self.animation = None
        self.spritesheet = spritesheet
        self.moves_buffer = []
        self.set_move(datas["default_move"])

    def unhold(self, unholdable):
        if self.animation.hold is False:
            return
        self.animation.hold = self.animation.name not in unholdable

    def propose_moves(self, moves):
        for move in moves:
            if is_move_change_authorized(move, self.datas, self.animation):
                self.set_move(move)
                return
            conditions = (
                self.animation.bufferable and
                move not in self.moves_buffer and
                self.animation.name != move and
                self.animation.loop_on != move)
            if conditions:
                self.moves_buffer.insert(0, move)

    def set_move(self, move):
        self.moves_buffer = []
        if self.animation is not None:
            for event, value in self.animation.post_events.items():
                self.apply_event(event, value)
        mirror = self.cordinates.mirror
        self.animation = self.spritesheet.build_animation(move, mirror)
        for event, value in self.animation.pre_events.items():
            self.apply_event(event, value)

    def apply_event(self, event, value):
        if event == EVENTS.BLOCK_OFFSET:
            mirror = self.cordinates.mirror
            block_offset = (-value[0], -value[1]) if mirror is True else value
            self.cordinates.block_position[0] += block_offset[0]
            self.cordinates.block_position[1] += block_offset[1]
        elif event == EVENTS.FLIP:
            self.cordinates.mirror = not self.cordinates.mirror
        elif event == EVENTS.SWITCH_TO:
            filename = os.path.join(wctx.MOVE_FOLDER, value)
            self.spritesheet = SpriteSheet.from_filename(filename)
            with open(filename, 'r') as f:
                self.datas = json.load(f)

    def set_next_move(self):
        next_move = self.datas["moves"][self.animation.name]["next_move"]
        if self.moves_buffer:
            key = "animation_in"
            for move in self.moves_buffer:
                moves_filter = self.datas["moves"][move]["conditions"].get(key)
                conditions = (
                    moves_filter is not None and
                    self.animation.name not in moves_filter and
                    next_move not in moves_filter)
                if conditions:
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
            self.set_move(self.animation.loop_on)
        self.animation.next()
        self.cordinates.center_offset = map_point(
            self.animation.center,
            self.datas["block_size"],
            self.cordinates.mirror)

    @property
    def trigger(self):
        return self.animation.trigger

    @property
    def image(self):
        return self.animation.image


def map_point(point, size, mirror):
    if mirror is False:
        return point
    return [size[0] - point[0], point[1]]