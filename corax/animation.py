"""
This Animation module provides functions and object to handle sprite animation
and sprisheet representations.
A sprite sheet is an image containing multiples frame off a sprites. Those
images are multiple animations. The sprites sheet data are a json containing
all frame informations necessary to create an animation object.
"""

from corax.coordinate import map_pixel_position, to_block_size
from corax.mathutils import sum_num_arrays
from corax.override import load_json
from corax.pygameutils import load_images, image_mirror


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
            "hitmaps": {str: [[(int, int), ...], [(int, int), ...], ...]}
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
        if not images:
            raise ValueError(f"No image providen to build animation {name}")
        self.name = name
        self.release_frame = data.get("release_frame", -1)
        self.pre_events = data["pre_events"]
        self.post_events = data["post_events"]
        self.bufferable = data["next_move_bufferable"]
        self.index = -1
        self.centers = build_centers_list(data, size, flip)
        self.sequences = [build_sequence(data, imgs) for imgs in images]
        self.hold = data["hold"]
        self.next_move = data["next_move"]
        self.loop_on = data["loop_on"]
        self.repeatable = data["loop_on"] is not None
        self.hitmaps_sequence = build_hitmaps_sequence(data, size, flip)
        self.triggers = build_triggers_list(data)

    @property
    def length(self):
        return len(self.sequences[0])

    def is_lock(self):
        if self.release_frame == -1:
            return not self.is_finished()
        return self.index < self.release_frame

    def is_finished(self):
        return self.index + 1 == len(self.sequences[0])

    def is_playing(self):
        return not self.is_finished() and self.index >= 0

    def evaluate(self):
        if self.is_finished() is False:
            self.index += 1
        return self.images

    @property
    def pixel_center(self):
        return None if self.index < 0 else self.centers[self.index]

    @property
    def trigger(self):
        return None if self.index < 0 else self.triggers[self.index]

    @property
    def images(self):
        if self.index < 0:
            return None
        return [images[self.index] for images in self.sequences]

    @property
    def hitmaps(self):
        if self.index < 0 or self.hitmaps_sequence is None:
            return None
        return {k: v[self.index] for k, v in self.hitmaps_sequence.items()}


class SpriteSheet():
    # NOTE: Keep an eye on this class. It contains only 3 functions which 2 are
    # constructors. At some point, if it appears that no other method is
    # necessary, I should considerate to replace it by a function.
    """
    This class represent a collection of animations. That very simple manager
    is able to create an animation on demand from his collections of image.
    """
    def __init__(self, name, data, sequences):
        self.name = name
        self.data = data
        self.moves_data = data["moves"]
        self.sequences = sequences
        self.sequences_mirror = {
            layer: [image_mirror(image) for image in images]
            for layer, images in self.sequences.items()}

    @staticmethod
    def from_filename(name, filename):
        data = load_json(filename)
        frame_size = data["frame_size"]
        key_color = data["key_color"]
        sequences = {
            layer: load_images(filename, frame_size, key_color)
            for layer, filename in data["layers"].items()}
        return SpriteSheet(name, data, sequences)

    def build_animation(self, move, flip, layer_names=None):
        assert layer_names
        assert self.sequences

        sequences = self.sequences_mirror if flip else self.sequences
        sequences = [sequences[layer] for layer in layer_names if sequences.get(layer)]
        if not sequences:
            msg = f"No image found for {self.name}, {move}. "
            msg += "May no valid layer for the current sheet is found."
            raise Exception(msg)
        try:
            data = self.data["moves"][move]
        except KeyError:
            keys = ", ".join(str(k) for k in self.data["moves"].keys())
            raise KeyError(f"{keys} doesn't contains {move}")
        size = self.data["frame_size"]
        return Animation(move, sequences, data, size, flip)


def build_triggers_list(data):
    """
    Build a triggers list base on animation data.
    Example if data contains those keys/values:
        "triggers": [(4, "boum"), (6, "step_foot")]
        "frames_per_image": [2, 1, 1, 3]"
    The function will returns:
    [None, None, None, None, "boum", None, "step_foot", None]
    """
    if not data["triggers"]:
        return [None for d in (data["frames_per_image"]) for _ in range(d)]

    triggers_data = {t[0]: t[1] for t in data["triggers"]}
    result = []
    for i, d in enumerate(data["frames_per_image"]):
        for _ in range(d):
            trigger = triggers_data.get(i)
            result.append(trigger)
            if trigger:
                del triggers_data[i]
    return result


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


def build_sequence(data, images):
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
    Build a list of (int, int) pixel positions indicating the center of each
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


def build_hitmaps_sequence(data, size, flip):
    """
    Build a list of hitbocks corresponding to the frame data and flipped if
    necessary."""
    size = to_block_size(size)
    try:
        return {
            name: [
                [map_pixel_position(block, size, flip) for block in hitmap[i]]
                for i, d in enumerate(data["frames_per_image"])
                for _ in range(d)]
            for name, hitmap in (data.get("hitmaps", {}) or {}).items()}
    except IndexError as e:
        import traceback
        msg = traceback.format_exc()
        raise IndexError("Wrong hitmap for " + str(data) + "\n" + msg)



def animation_index_to_data_index(index, data):
    """
    Animation index is the index of a frame in 30 fps. Each frame is one index.
    Data index is the corresponding index in the frame data sheet. Only unique
    drawn frame are stored. But each frame can have different duration.
    This convert the animation index to the data one.
    Example:
    Data indexes:
    0           1     2                 3                 4  ..
    Animation indexes:
    0  -  1  -  2  -  3  -  4  -  5  -  6  -  7  -  8  -  9  ...
    in data indexes, frame 0 has a 2 frames duration, 1 has 1 and 2 has 3.
    Return examples:
         index = 5 -> 2
         index = 7 -> 3
         index = 1 -> 0
    """
    loop = 0
    for i, d in enumerate(data["frames_per_image"]):
        for _ in range(d):
            if index == loop:
                return i
            loop += 1


def data_index_to_animation_index(index, data):
    """
    This is the reverse remap than animation_index_to_data_index()
    This convert the data index to the animation one.
    Example:
    Data indexes:
    0           1     2                 3                 4  ...
    Animation indexes:
    0  -  1  -  2  -  3  -  4  -  5  -  6  -  7  -  8  -  9  ...
    in data indexes, frame 0 has a 2 frames duration, 1 has 1 and 2 has 3.
    Return examples:
         index = 1 -> 2
         index = 3 -> 6
         index = 8 -> 3
    """
    loop = 0
    for i, d in enumerate(data["frames_per_image"]):
        for _ in range(d):
            if index == i:
                return loop
            loop += 1
    frames = str(data["frames_per_image"])
    msg = f"Index math not found for {index} to {frames}"
    raise ValueError(msg)
