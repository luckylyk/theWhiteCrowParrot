
import json
from corax.pygameutils import load_images, image_mirror


def build_triggers_list(datas):
    length = len(
        [None for i, d in enumerate(datas["frames_per_image"])
        for _ in range(d)])
    if datas["triggers"] is None:
        return [None for _ in range(length)]
    triggers = {t[0]: t[1] for t in datas["triggers"]}
    return [triggers[i] if i in triggers else None for i in range(length)]


def build_images_list(datas, images):
    return [
        images[i + datas["start_at_image"]]
        for i, d in enumerate(datas["frames_per_image"])
        for _ in range(d)]


def build_centers_list(datas):
    default_center = datas["center"]
    frame_centers = datas.get("frames_centers")
    if frame_centers is None:
        return [
            default_center for i, d in enumerate(datas["frames_per_image"])
            for _ in range(d)]
    centers = []
    for i, d in enumerate(datas["frames_per_image"]):
        x = default_center[0] + frame_centers[i][0]
        y = default_center[1] + frame_centers[i][1]
        center = [x, y]
        for _ in range(d):
            centers.append(center)
    return centers


class Animation():
    def __init__(self, name, images, datas):
        self.name = name
        self.release_frame = datas.get("release_frame", -1)
        self.pre_events = datas["pre_events"]
        self.post_events = datas["post_events"]
        self.bufferable = datas["next_move_bufferable"]
        self.index = -1
        self.centers = build_centers_list(datas)
        self.images = build_images_list(datas, images)
        self.hold = datas["hold"]
        self.next_move = datas["next_move"]
        self.loop_on = datas["loop_on"]
        self.repeatable = datas["loop_on"] is not None
        self.triggers = build_triggers_list(datas)

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
        return self.image

    @property
    def center(self):
        if self.index < 0:
            return None
        return self.centers[self.index]

    @property
    def trigger(self):
        if self.index < 0:
            return None
        return self.triggers[self.index]

    @property
    def image(self):
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
    def from_filename(filename):
        with open(filename) as f:
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

