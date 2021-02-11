"""
This Animation module provides functions and object to handle sprite animation
and sprisheet representations.
A sprite sheet is an image containing multiples frame off a sprites. Those
images are multiple animations. The sprites sheet datas are a json containing
all frame informations necessary to create an animation object.
"""
import json
from corax.pygameutils import load_images, image_mirror
from corax.mathutils import sum_num_arrays
from corax.cordinates import map_pixel_position


class Animation():
    """
    Animation class is the visual representation of a sprite. It allow the
    engine to control the current image using some frame datas providen during
    object initialisation. The datas structure of an animation is a dictionary
    following that template:
        {
            "start_at_image": int,
            "center": [int, int],
            "frames_per_image": [int, int, int, ...],
            "triggers": [(int, str), (int, str), (int, str), ...],
            "frames_centers": [(int, int), (int, int), ...],
            "release_frame": int,
            "hold": bool,
            "next_move": str,
            "next_move_bufferable": bool,
            "loop_on": str,
            "inputs": [str, ...],
            "conditions": dict,
            "pre_events": dict,
            "post_events": dict
        }
    this is the dictionnary key purpose:
    - start_frame: the first frame in the sprite sheet (unused by Animation())
    - center: global pixel position of image center. This is necessary to
    evaluate the offset when the animation is flipped
    - frame_per_image: define the frame duration per images.
    - triggers: list (frame, "trigger name") can be listened externally to
    trigger some events or sounds
    - frames_centers: list of pixel positions representing a center offset
    per frame.
    - release_frame: this is the frame index where the animation can be cut by
    another one. -1 means that can't be cut at all.
    - hold: set the Animation.hold variable
    - next_move: the off the animation which naturally to follow the current
    one by default.
    - next_move_bufferable: this attribute tells if next move request can be
    recorded during this animation is player.
    - loop_on: name on the animation which follow if the current one is on hold
    when it is finished
    - conditions: list of conditions neceray to autorise this animation
    (unused by Animation())
    - post_event: dict of events has to be executed when animation is finished
    - pre_event: dict of events has to be executed before the animation starts
    """
    def __init__(self, name, images, datas, size, flip=False):
        self.name = name
        self.release_frame = datas.get("release_frame", -1)
        self.pre_events = datas["pre_events"]
        self.post_events = datas["post_events"]
        self.bufferable = datas["next_move_bufferable"]
        self.index = -1
        self.centers = build_centers_list(datas, size, flip)
        self.images = build_images_list(datas, images)
        self.hold = datas["hold"]
        self.next_move = datas["next_move"]
        self.loop_on = datas["loop_on"]
        self.repeatable = datas["loop_on"] is not None
        self.triggers = build_triggers_list(datas)

    @property
    def length(self):
        return len(self.images)

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
    def pixel_center(self):
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
    """
    This class represent a collection of animations. That very simple manager
    is able to create an animation on demand from his collections of image.
    """
    def __init__(self, name, datas, images):
        self.name = name
        self.datas = datas
        self.moves_datas = datas["moves"]
        self.images = images
        self.images_mirror = [image_mirror(img) for img in self.images]

    @staticmethod
    def from_filename(name, filename):
        with open(filename) as f:
            datas = json.load(f)
        filename = datas["filename"]
        image_size = datas["image_size"]
        key_color = datas["key_color"]
        images = load_images(filename, image_size, key_color)
        return SpriteSheet(name, datas, images)

    def build_animation(self, move, flip):
        images = self.images_mirror if flip else self.images
        datas = self.datas["moves"][move]
        size = self.datas["image_size"]
        return Animation(move, images, datas, size, flip)


def build_triggers_list(datas):
    """
    Build a triggers list base on animation datas.
    Example if data contains those keys/values:
        "triggers": [(4, "boum"), (6, "step_foot")]
        "frames_per_image": [2, 1, 1, 3]"
    The function will returns:
    [None, None, None, None, "boum", None, "step_foot", None]
    """
    length = len(
        [None for i, d in enumerate(datas["frames_per_image"])
        for _ in range(d)])
    if datas["triggers"] is None:
        return [None for _ in range(length)]
    triggers = {t[0]: t[1] for t in datas["triggers"]}
    return [triggers[i] if i in triggers else None for i in range(length)]


def build_images_list(datas, images):
    """
    Build of images from the spreadsheet image list based on a animation datas.
    Basically it also duplicate the frames base on a data when it is necessary
    to match the frame counts.
    Example if data contains those keys/values:
        "start_at_image": 10
        "frames_per_image": [2, 1, 1, 3]
    The function will returns:
    [image_10, image_10, image_11, image_12, image_13, image_13, image_13]
    """
    return [
        images[i + datas["start_at_image"]]
        for i, d in enumerate(datas["frames_per_image"])
        for _ in range(d)]


def build_centers_list(datas, size, flip):
    """
    build a list of (int, int) pixel positions indicating the center of each
    frame.
    """
    default_center = datas["center"]
    frame_centers = datas.get("frames_centers")
    if frame_centers is None:
        default_center = map_pixel_position(default_center, size, flip)
        return [
            default_center for i, d in enumerate(datas["frames_per_image"])
            for _ in range(d)]
    centers = []
    for i, d in enumerate(datas["frames_per_image"]):
        center = sum_num_arrays(default_center, frame_centers[i])
        center = map_pixel_position(center, size, flip)
        for _ in range(d):
            centers.append(center)
    return centers
