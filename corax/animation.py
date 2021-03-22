"""
This Animation module provides functions and object to handle sprite animation
and sprisheet representations.
A sprite sheet is an image containing multiples frame off a sprites. Those
images are multiple animations. The sprites sheet data are a json containing
all frame informations necessary to create an animation object.
"""
import json
from corax.pygameutils import load_images, image_mirror
from corax.mathutils import sum_num_arrays
from corax.coordinates import map_pixel_position


class Animation():
    """
    Animation class is the visual representation of a sprite. It allow the
    engine to control the current image using some frame data providen during
    object initialisation. The data structure of an animation is a dictionary
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
    def __init__(self, name, images, data, size, flip=False):
        self.name = name
        self.release_frame = data.get("release_frame", -1)
        self.pre_events = data["pre_events"]
        self.post_events = data["post_events"]
        self.bufferable = data["next_move_bufferable"]
        self.index = -1
        self.centers = build_centers_list(data, size, flip)
        self.images = build_images_list(data, images)
        self.hold = data["hold"]
        self.next_move = data["next_move"]
        self.loop_on = data["loop_on"]
        self.repeatable = data["loop_on"] is not None
        self.triggers = build_triggers_list(data)

    @property
    def length(self):
        return len(self.images)

    def is_lock(self):
        if self.release_frame == -1:
            return not self.is_finished()
        return self.index < self.release_frame

    def is_finished(self):
        return self.index + 1 == len(self.images)

    def is_playing(self):
        return not self.is_finished() and self.index >= 0

    def evaluate(self):
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
    def __init__(self, name, data, images):
        self.name = name
        self.data = data
        self.moves_datas = data["moves"]
        self.images = images
        self.images_mirror = [image_mirror(img) for img in self.images]

    @staticmethod
    def from_filename(name, filename):
        with open(filename) as f:
            data = json.load(f)
        filename = data["filename"]
        frame_size = data["frame_size"]
        key_color = data["key_color"]
        images = load_images(filename, frame_size, key_color)
        return SpriteSheet(name, data, images)

    def build_animation(self, move, flip):
        images = self.images_mirror if flip else self.images
        data = self.data["moves"][move]
        size = self.data["frame_size"]
        return Animation(move, images, data, size, flip)


def build_triggers_list(data):
    """
    Build a triggers list base on animation data.
    Example if data contains those keys/values:
        "triggers": [(4, "boum"), (6, "step_foot")]
        "frames_per_image": [2, 1, 1, 3]"
    The function will returns:
    [None, None, None, None, "boum", None, "step_foot", None]
    """
    length = len(
        [None for i, d in enumerate(data["frames_per_image"])
        for _ in range(d)])
    if data["triggers"] is None:
        return [None for _ in range(length)]
    triggers = {t[0]: t[1] for t in data["triggers"]}
    return [triggers[i] if i in triggers else None for i in range(length)]


def build_images_list(data, images):
    """
    Build of images from the spreadsheet image list based on a animation data.
    Basically it also duplicate the frames base on a data when it is necessary
    to match the frame counts.
    Example if data contains those keys/values:
        "start_at_image": 10
        "frames_per_image": [2, 1, 1, 3]
    The function will returns:
    [image_10, image_10, image_11, image_12, image_13, image_13, image_13]
    """
    return [
        images[i + data["start_at_image"]]
        for i, d in enumerate(data["frames_per_image"])
        for _ in range(d)]


def build_centers_list(data, size, flip):
    """
    build a list of (int, int) pixel positions indicating the center of each
    frame.
    """
    default_center = data["center"]
    frame_centers = data.get("frames_centers")
    if frame_centers is None:
        default_center = map_pixel_position(default_center, size, flip)
        return [
            default_center for i, d in enumerate(data["frames_per_image"])
            for _ in range(d)]
    centers = []
    for i, d in enumerate(data["frames_per_image"]):
        center = sum_num_arrays(default_center, frame_centers[i])
        center = map_pixel_position(center, size, flip)
        for _ in range(d):
            centers.append(center)
    return centers
