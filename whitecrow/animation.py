
import os

from whitecrow.iterators import frame_data_iterator
from whitecrow.options import ROOT


class Signal():
    def __init__(self):
        self._functions = []

    def emit(self, *args, **kwargs):
        for func in self._functions:
            func(*args, **kwargs)

    def connect(self, func):
        self._functions.append(func)


class AnimationSheet(object):
    def __init__(self, animationsheet_data, images):
        self.animationsheet_data = animationsheet_data
        self.images = images

        self.block_offset_requested = Signal()

        self.is_lock = False
        self.hold = False
        self.animation_data = None
        self.current_animation = None
        self._frame_data_iterator = None
        self._frame_data_index = None
        self.do_offset = False
        self.block_offset = [0, 0]
        self.k = 0

        self.set_animation(self.animationsheet_data["default_animation"])

    def unlock(self):
        self.locked = False

    def lock(self):
        self.locked = True

    def set_next_animation(self):
        default = self.animationsheet_data["default_animation"]
        animation_name = self.animation_data.get("goeson", default)
        self.set_animation(animation_name)

    def is_playing(self, animation_name):
        return self.current_animation == animation_name

    def set_animation(self, animation_name):
        if self.is_lock:
            return
        if self.animation_data and self.animation_data.get("post_blockoffset"):
            blockoffset = self.animation_data["post_blockoffset"]
            self.block_offset_requested.emit(blockoffset)

        self.current_animation = animation_name
        data = self.animationsheet_data["animations"][animation_name]
        self.animation_data = data
        data = self.animation_data["frames"]
        self._frame_data_iterator = frame_data_iterator(data)
        self.hold = self.animation_data["hold"]
        self._frame_data_index = 0
        self._previous_frame_data_index = None

        if self.animation_data.get("pre_blockoffset") is not None and self.do_offset is False:
            blockoffset = self.animation_data["pre_blockoffset"]
            self.block_offset_requested.emit(blockoffset)
        self.lock()
        return

    def next_frame(self):
        self._previous_frame_data_index = self._frame_data_index
        try:
            self._frame_data_index = next(self._frame_data_iterator)
        except StopIteration:
            if self.hold is False:
                self.set_next_animation()
        self.update_states()

    def update_states(self):
        frame = self.animation_data["frames"][self._frame_data_index]
        if frame.get("cancellable") is True:
            self.unlock()

    @property
    def current_image(self):
        index = self.animation_data["startframe"] + self._frame_data_index
        return self.images[index]
