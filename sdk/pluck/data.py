
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
ZONE_TYPES = (
    NODE_TYPES.NO_GO,
    NODE_TYPES.INTERACTION,
    NODE_TYPES.RELATIONSHIP,
    NODE_TYPES.COLLIDER)
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
    "hitmaps": None}


DATA_TEMPLATES = {
    "game_settings": {
        "title": str,
        "start_scene": str,
        "start_scrolling_targets": {str},
        "fade_in_duration": int
    },
    "game_preferences": {
        "resolution": (int, int),
        "fps": int,
        "block_size": 10,
        "key_color": (int, int, int),
        "camera_speed": int
    },
    "spritesheet": {
        "layers": None,
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
        "hitmaps": None
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
    "collider": {
        "type": str,
        "name": str,
        "affect": {str},
        "hitmaps": {str},
        "event": str,
        "zone": (int, int, int, int),
    },
    "relationship": {
        "enable": bool,
        "type": str,
        "name": str,
        "subject": str,
        "target": str,
        "relationship": str,
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
    "npc": {
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


def plain_text_to_data(plain_text):
    return json.loads(plain_text)


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
            value = "null"
        elif value is True:
            value = "true"
        elif value is False:
            value = "false"
        elif value == {}:
            value = "{}"
        elif isinstance(value, dict):
            value = data_to_plain_text(
                value, indent=indent+1, sorted_keys=key not in DONT_SORT_KEYS)

        lines.append(f"    \"{key}\": {value}".replace("'", '"'))
    spacer = "    " * indent
    return f"{{\n{spacer}" + f",\n{spacer}".join(lines) + f"\n{spacer}}}"
