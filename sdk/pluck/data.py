
import os
import json
from corax.core import NODE_TYPES


KEY_ORDER = "name", "type", "file", "position"
ROOT_SUBFOLDERS =(
    "animations",
    "players",
    "scripts",
    "scenes",
    "sets",
    "sheets",
    "sounds")

DONT_SORT_KEYS = "post_events", "pre_events"
EXCLUDED_PROPERTIES = "sounds", "areas", "elements", "zones"
GRAPHIC_TYPES = NODE_TYPES.SET_ANIMATED, NODE_TYPES.SET_STATIC, NODE_TYPES.PLAYER
SET_TYPES = NODE_TYPES.SET_ANIMATED, NODE_TYPES.SET_STATIC
ZONE_TYPES = NODE_TYPES.NO_GO, NODE_TYPES.INTERACTION
SOUND_TYPES = (
    NODE_TYPES.SFX,
    NODE_TYPES.AMBIANCE,
    NODE_TYPES.MUSIC,
    NODE_TYPES.SFX_COLLECTION)

DEFAULT_MOVE = {
    "start_at_image": 0,
    "center": [0, 0],
    "frames_per_image": [1],
    "triggers": None,
    "frames_centers": None,
    "release_frame": -1,
    "next_move": "idle",
    "next_move_bufferable": False,
    "hold": False,
    "loop_on": "idle",
    "conditions": {},
    "inputs": [],
    "pre_events": {},
    "post_events": {},
    "hitboxes": None}

DATA_TEMPLATES = {
    "spritesheet": {
        "filename": str,
        "key_color": (int, int, int),
        "frame_size": (int, int),
        "default_move": str,
        "evaluation_order": {str},
        "moves": None
    },
    "move": {
        "start_at_image": int,
        "center": (int, int),
        "frames_per_image": {int},
        "triggers": {(int, str)},
        "frames_centers": {(int, int)},
        "release_frame": int,
        "next_move": str,
        "next_move_bufferable": bool,
        "hold": bool,
        "loop_on": str,
        "conditions": None,
        "inputs": {str},
        "pre_events": None,
        "post_events": None,
        "hitboxes": None
    },
    "scene": {
        "name": str,
        "type": str,
        "background_color": (int, int, int),
        "boundary": (int, int, int, int),
        "soft_boundaries": {(int, int, int, int)},
        "target_offset": (int, int)
    },
    "no_go": {
        "type": str,
        "name": str,
        "affect": {str},
        "zone": (int, int, int, int),
    },
    "interaction": {
        "type": str,
        "name": str,
        "affect": {str},
        "scripts": {str},
        "zone": (int, int, int, int),
    },
    "ambiance": {
        "name": str,
        "type": str,
        "file": str,
        "channel": int,
        "falloff": int,
        "listener": str,
        "zone": (int, int, int, int)
    },
    "music": {
        "name": str,
        "type": str,
        "file": str,
        "channel": int,
        "falloff": int,
        "listener": str,
        "zone": (int, int, int, int)
    },
    "sfx_sound_collection": {
        "name": str,
        "type": str,
        "emitter": str,
        "channel": int,
        "falloff": int,
        "files": {str},
        "order": str,
        "trigger": str,
        "zone": (int, int, int, int)
    },
    "sfx_sound": {
        "name": str,
        "type": str,
        "emitter": str,
        "falloff": int,
        "channel": int,
        "file": str,
        "trigger": str,
        "zone": (int, int, int, int)
    },
    "layer": {
        "name": str,
        "type": str,
        "deph": float
    },
    "set_static":{
        "name": str,
        "type": str,
        "file": str,
        "position": (int, int),
        "deph": float,
    },
    "set_animated": {
        "name": str,
        "type": str,
        "file": str,
        "position": (int, int),
        "alpha": int,
        "deph": float
    },
    "player": {
        "name": str,
        "type": str,
        "block_position": (int, int),
        "flip": bool
    },
    "particles_system": {
        "name": str,
        "alpha": int,
        "type": str,
        "direction_options": {
            "rotation_range": int,
            "speed": int},
        "deph": float,
        "emission_positions": None,
        "emission_zone": None,
        "flow": int,
        "shape_options": {
            "type": str,
            "alpha": (int, int),
            "color": (int, int, int),
            "size": int},
        "spot_options": {
            "boundary_behavior": str,
            "frequency": (int, int),
            "speed": (float, float)},
        "start_number": int,
        "zone": (int, int, int, int)
    }
}


def create_project(root):
    for folder in ROOT_SUBFOLDERS:
        os.mkdir(os.path.join(root, folder))


def tree_sanity_check(tree):
    nodes = tree.flat()
    for node in nodes:
        if node.data is None:
            continue
        data_sanity_check(node.data)


def data_sanity_check(data, type_=None):
    assert isinstance(data, dict), "data as to be a dict"
    type_ = type_ or data.get("type")
    assert type_ in DATA_TEMPLATES, f"{type_} is not a valid node type"
    template = DATA_TEMPLATES[type_]
    for key in template.keys():
        assert key in data.keys(), f"Missing parameter: {key}"
    for key in data.keys():
        assert key in template.keys(), f"Invalid parameter: {key}"
    for key, value in data.items():
        if value is None:
            continue
        type_required = template[key]
        if type_required is None:
            continue
        test_type_required(key, value, type_required)


def test_type_required(key, value, type_required):
    conditions = (
        type_required in [int, float, str, None] and
        not isinstance(value, type_required))
    assert not conditions, f"'{key}' must be a {str(type_required)} value, but is {type(key)}"

    if isinstance(type_required, (list, tuple)):
        assert len(value) == len(type_required), f"'{key}' types must match {type_required}"
        try:
            for v, t in zip(value, type_required):
                assert isinstance(v, t), f"'{value}' types must match {type_required}, but get {type(v)}"
        except:
            msg = f"'{value}' types must match {type_required}"
            raise TypeError(msg)

    elif isinstance(type_required, dict):
        for k, v in value.items():
            if v is None:
                continue
            t = type_required[k]
            test_type_required(k, v, t)

    elif isinstance(type_required, set):
        for v in value:
            for t in type_required:
                test_type_required(key, v, t)


def extract_scene_properties(scene_data):
    return {
        k: v for k, v in scene_data.items()
        if k not in EXCLUDED_PROPERTIES}


def sort_keys(elements):
    copy = []
    for key in KEY_ORDER:
        if key in elements:
            copy.append(key)
            elements.remove(key)
    return copy + sorted(elements)


def data_to_plain_text(data, indent=0, sorted_keys=True):
    if sorted_keys:
        keys = sort_keys([str(key) for key in data.keys()])
    else:
        keys = [str(key) for key in data.keys()]
    lines = []
    for key in keys:
        value = data[key]
        if isinstance(value, str):
            value = f"\"{value}\""
        elif value is None:
            value = " null"
        elif value is True:
            value = " true"
        elif value is False:
            value = " false"
        elif value == {}:
            value = "{}"
        elif isinstance(value, dict):
            value = data_to_plain_text(
                value, indent=indent+2, sorted_keys=key not in DONT_SORT_KEYS)
        lines.append(f"    \"{key}\": {value}".replace("'", '"'))
    spacer = "    " * indent
    return f"{{\n{spacer}" + f",\n{spacer}".join(lines) + f"\n{spacer}}}"


def plain_text_to_data(plain_text):
    return json.loads(plain_text)