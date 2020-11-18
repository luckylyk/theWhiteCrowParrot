from whitecrow.core import Signal
import json
from whitecrow.graphicutils import load_images, image_mirror


class Animation():

    def __init__(self, name, images, datas):
        self.name = name
        self.finished = Signal()
        self.release_frame = datas.get("release_frame", -1)
        self.pre_events = datas["pre_events"]
        self.post_events = datas["post_events"]
        self.bufferable = datas["next_move_bufferable"]
        self.index = -1
        self.indexes = [
            [i + datas["start_at_image"]]
            for i, d in enumerate(datas["frames_per_image"])
            for _ in range(d)]
        self.images = [
            images[i + datas["start_at_image"]]
            for i, d in enumerate(datas["frames_per_image"])
            for _ in range(d)]
        self.hold = datas["hold"]
        self.next_move = datas["next_move"]
        self.repeatable = datas["repeatable"]

    def is_lock(self):
        if self.release_frame == -1:
            return not self.is_finished()
        return self.index >= self.release_frame

    def is_finished(self):
        return self.index + 1 == len(self.images)

    def is_playing(self):
        return not self.is_finished() and self.index >= 0

    def next(self):
        if self.is_finished() is False:
            self.index += 1
        elif self.hold is False:
            self.finished.emit()
        return self.current_image

    @property
    def current_image(self):
        if self.index < 0:
            return None
        return self.images[self.index]


class SpriteSheet():
    def __init__(self, datas, images):
        self.datas = datas
        self.moves_datas = datas["moves"]
        self.images = images
        self.images_mirror = [image_mirror(img) for img in self.images]

    @staticmethod
    def from_datafile(filepath):
        with open(filepath) as f:
            data = json.load(f)
        filename = data["filename"]
        block_size = data["block_size"]
        key_color = data["key_color"]
        images = load_images(filename, block_size, key_color)
        return SpriteSheet(data, images)

    def build_animation(self, move, mirror):
        images = self.images_mirror if mirror else self.images
        datas = self.datas["moves"][move]
        return Animation(move, images, datas)

