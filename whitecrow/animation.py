
import os
import json

from whitecrow.iterators import frame_data_iterator
from whitecrow.options import ROOT
from whitecrow.graphicutils import load_images, image_mirror


class Signal():
    def __init__(self):
        self._functions = []

    def emit(self, *args, **kwargs):
        for func in self._functions:
            func(*args, **kwargs)

    def connect(self, func):
        self._functions.append(func)


class MoveSheet(object):
    def __init__(self, data, images):
        self.data = data
        self.images = images
        self.images_mirror = [image_mirror(img) for img in self.images]
        self.mirror = False

        self.block_offset_requested = Signal()
        self.do_mirror = Signal()

        self.is_lock = False
        self.hold = False
        self.move_data = None
        self.current_move = None
        self._frame_data_iterator = None
        self._frame_data_index = None
        self.do_offset = False
        self.block_offset = [0, 0]
        self.k = 0

        self.set_move(self.data["default_move"])

    @staticmethod
    def from_json(filepath):
        with open(filepath) as f:
            data = json.load(f)
        filename = data["filename"]
        block_size = data["block_size"]
        key_color = data["key_color"]
        images = load_images(filename, block_size, key_color)
        return MoveSheet(data, images)

    def iter_move_datas(self):
        for move in self.data["move_priority"]:
            yield move, self.data["moves"][move]

    def unlock(self):
        self.locked = False

    def lock(self):
        self.locked = True

    def set_next_move(self):
        default = self.data["default_move"]
        move_name = self.move_data.get("goeson", default)
        self.set_move(move_name)

    def is_playing(self, move_name):
        return self.current_move == move_name

    def map_offset(self, offset):
        if self.mirror is False:
            return offset
        return [-offset[0], -offset[1]]

    def set_move(self, move_name):
        if self.is_lock:
            return

        if self.move_data and self.move_data.get("post_blockoffset"):
            blockoffset = self.map_offset(self.move_data["post_blockoffset"])
            self.block_offset_requested.emit(blockoffset)

        if self.move_data and self.move_data.get("post_mirror"):
            self.do_mirror.emit()

        self.current_move = move_name
        data = self.data["moves"][move_name]
        self.move_data = data
        data = self.move_data["frames"]
        self._frame_data_iterator = frame_data_iterator(data)
        self.hold = self.move_data["hold"]
        self._frame_data_index = 0
        self._previous_frame_data_index = None

        if self.move_data.get("pre_blockoffset") is not None:
            blockoffset = self.map_offset(self.move_data["pre_blockoffset"])
            self.block_offset_requested.emit(blockoffset)
        self.lock()
        return

    def next_frame(self):
        self._previous_frame_data_index = self._frame_data_index
        try:
            self._frame_data_index = next(self._frame_data_iterator)
        except StopIteration:
            if self.hold is False:
                self.set_next_move()
        self.update_states()

    def update_states(self):
        frame = self.move_data["frames"][self._frame_data_index]
        if frame.get("cancellable") is True:
            self.unlock()

    @property
    def current_image(self):
        index = self.move_data["startframe"] + self._frame_data_index
        if self.mirror is True:
            return self.images_mirror[index]
        return self.images[index]
