"""
This Animation module provides functions and object to handle sprite animation
and sprisheet representations.
A sprite sheet is an image containing multiples frame off a sprites. Those
images are multiple animations. The sprites sheet data are a json containing
all frame informations necessary to create an animation object.
"""
import json
from corax.coordinate import map_pixel_position
from corax.mathutils import sum_num_arrays
from corax.pygameutils import load_images, image_mirror


class AnimationController():
    """
    The animation controller (this name sucks, I have to find a better one) is an
    object with manage the animations sequences and how they chains. It verify
    what are the next animation possible using the conditions filters,
    the movement predictions (to manage the environment boundaries),
    check the gamepad input, animation states (on hold, repeatable,
    cancelable, etc ...).
    The data comes from the JSON set in the <root>/moves folder. It is
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
    - moves: move data by move name. For more details on frame data
    dictionnary structure see the class corax.animation.Animation.
    """
    def __init__(self, data, spritesheet, coordinate, layers=None):
        self.animation = None
        self.coordinate = coordinate
        self.data = data
        self.no_go_zones = []
        self.layers = layers or [str(key) for key in spritesheet.data["layers"].keys()]
        self.moves_buffer = []
        self.sequence = []
        self.spritesheet = spritesheet
        self.set_move(data["default_move"])

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
                is_moves_sequence_valid(move, self.data, self.animation) and
                is_layers_authorized(move, self.data, self.layers) and
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
        block_position = self.coordinate.block_position
        block_offset = self.animation.post_events.get(EVENTS.BLOCK_OFFSET)
        flip_event = self.animation.post_events.get(EVENTS.FLIP)
        flip = not self.coordinate.flip if flip_event else self.coordinate.flip
        if block_offset:
            block_offset = flip_position(block_offset) if flip else block_offset
            block_position = sum_num_arrays(block_position, block_offset)
        return not is_move_cross_zone(
            move=move,
            image_size=self.data["frame_size"],
            block_position=block_position,
            flip=flip,
            data=self.data,
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

        flip = self.coordinate.flip
        layers = self.layers
        self.animation = self.spritesheet.build_animation(move, flip, layers)

        for event, value in self.animation.pre_events.items():
            self.apply_event(event, value)
            msg = f"EVENT: {self.animation.name}, {event}, {value}"
            logging.debug(msg)

    def flush(self):
        """
        This method immediatly reset animation state setting back the default
        move skipping the animation post event trigger. It usually triggered
        at scene change.
        """
        flip = self.coordinate.flip
        layers = self.layers
        move = self.data["default_move"]
        self.moves_buffer = []
        self.animation = self.spritesheet.build_animation(move, flip, layers)

    def apply_event(self, event, value):
        if event == EVENTS.BLOCK_OFFSET:
            flip = self.coordinate.flip
            block_offset = flip_position(value) if flip else value
            self.coordinate.block_position[0] += block_offset[0]
            self.coordinate.block_position[1] += block_offset[1]
        elif event == EVENTS.FLIP:
            self.coordinate.flip = not self.coordinate.flip
        elif event == EVENTS.SWITCH_TO:
            self.set_sheet(value)

    def set_sheet(self, filename, layers=None):
        self.layers = layers or self.layers
        filepath = os.path.join(cctx.SHEET_FOLDER, filename)
        self.spritesheet = SpriteSheet.from_filename(filename, filepath)
        with open(filepath, 'r') as f:
            self.data = json.load(f)

    def set_next_move(self):
        """
        This method is triggered when the current animation is done. This
        algorithme is looking in the buffer to find a valid sequence. If
        nothing is found, it does set the default animation next move.
        """
        if self.sequence:
            self.set_move(self.sequence.pop(0))
            # Loop animation sequences rely on hold attribute, force unhold
            # avoid this loop to happen and force the given sequence.
            self.animation.hold = False
            return

        next_move = self.animation.next_move
        if not self.moves_buffer:
            self.set_move(next_move)
            return

        for move in self.moves_buffer:
            conditions = (
                is_moves_sequence_valid(move, self.data, self.animation) and
                is_layers_authorized(move, self.data, self.layers) and
                self.is_offset_allowed(move))
            if not conditions:
                continue
            self.set_move(move)
            return

        self.set_move(next_move)

    def evaluate(self):
        anim = self.animation
        if anim.is_finished() and anim.hold is False:
            self.set_next_move()
        if anim.is_finished() and anim.hold is True and anim.repeatable:
            if self.sequence:
                self.set_next_move()
            # this repeat the current animation or next animation on the loop
            if self.is_offset_allowed(self.animation.loop_on):
                self.set_move(self.animation.loop_on)
            else:
                self.animation.hold = False
        self.animation.evaluate()
        self.coordinate.center_offset = self.animation.pixel_center

    @property
    def trigger(self):
        return self.animation.trigger

    @property
    def images(self):
        return self.animation.images

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
        self.sequences = [build_sequence(data, imgs) for imgs in images]
        self.hold = data["hold"]
        self.next_move = data["next_move"]
        self.loop_on = data["loop_on"]
        self.repeatable = data["loop_on"] is not None
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
        if self.index < 0:
            return None
        return self.centers[self.index]

    @property
    def trigger(self):
        if self.index < 0:
            return None
        return self.triggers[self.index]

    @property
    def images(self):
        if self.index < 0:
            return None
        return [images[self.index] for images in self.sequences]


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
        with open(filename) as f:
            data = json.load(f)
        frame_size = data["frame_size"]
        key_color = data["key_color"]
        sequences = {
            layer: load_images(filename, frame_size, key_color)
            for layer, filename in data["layers"].items()}
        return SpriteSheet(name, data, sequences)

    def build_animation(self, move, flip, layer_names=None):
        assert layer_names
        sequences = self.sequences_mirror if flip else self.sequences
        sequences = [sequences[layer] for layer in layer_names if sequences.get(layer)]
        data = self.data["moves"][move]
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
    length = len(
        [None for i, d in enumerate(data["frames_per_image"])
        for _ in range(d)])
    if data["triggers"] is None:
        return [None for _ in range(length)]
    triggers = {t[0]: t[1] for t in data["triggers"]}
    return [triggers[i] if i in triggers else None for i in range(length)]


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
