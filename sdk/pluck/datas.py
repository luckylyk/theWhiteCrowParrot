import json
from corax.core import NODE_TYPES


KEY_ORDER = "name", "type", "file", "position"
EXCLUDED_PROPERTIES = "sounds", "areas", "elements", "zones"
GRAPHIC_TYPES = NODE_TYPES.SET_ANIMATED, NODE_TYPES.SET_STATIC, NODE_TYPES.PLAYER
SET_TYPES = NODE_TYPES.SET_ANIMATED, NODE_TYPES.SET_STATIC
ZONE_TYPES = NODE_TYPES.NO_GO, NODE_TYPES.INTERACTION
SOUND_TYPES = (
    NODE_TYPES.SFX_COLLECTION,
    NODE_TYPES.SFX,
    NODE_TYPES.MUSIC,
    NODE_TYPES.AMBIANCE)

DATA_TEMPLATES = {
    "scene": {
        "name": str,
        "type": str,
        "background_color": (int, int, int),
        "boundary": (int, int, int, int),
        "grid_pixel_offset": (int, int),
        "scroll_target": str,
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
        "filename": str,
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
        "alpha": float,
        "deph": float
    },
    "player": {
        "name": str,
        "type": str,
        "block_position": (int, int),
        "movedatas_file": str
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


def tree_sanity_check(tree):
    nodes = tree.flat()
    for node in nodes:
        if node.data is None:
            continue
        data_sanity_check(node.data)


def data_sanity_check(data):
    if not isinstance(data, dict):
        raise ValueError("data as to be a dict")
    type_ = data.get("type")
    if type_ not in DATA_TEMPLATES:
        raise ValueError(f"{type_} is not a valid node type")
    template = DATA_TEMPLATES[data.get("type")]
    for key in template.keys():
        if key not in data.keys():
            raise KeyError(f"Missing parameter: {key}")
    for key in data.keys():
        if key not in template.keys():
            raise KeyError(f"Invalid parameter: {key}")
    for key, value in data.items():
        if value is None:
            continue
        type_required = template[key]
        test_type_required(key, value, type_required)


def test_type_required(key, value, type_required):
    conditions = (
        type_required in [int, float, str, None] and
        not isinstance(value, type_required))

    if conditions:
        raise TypeError(f"'{key}' must be a {str(type_required)} value")

    elif isinstance(type_required, (list, tuple)):
        if len(value) != len(type_required):
            msg = f"'{key}' types must match {type_required}"
            raise TypeError(msg)
        try:
            for v, t in zip(value, type_required):
                if not isinstance(v, t):
                    msg = f"'{value}' types must match {type_required}"
                    raise TypeError(msg)
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


def extract_scene_properties(scene_datas):
    return {
        k: v for k, v in scene_datas.items()
        if k not in EXCLUDED_PROPERTIES}


def sort_keys(elements):
    copy = []
    for key in KEY_ORDER:
        if key in elements:
            copy.append(key)
            elements.remove(key)
    return copy + sorted(elements)


def data_to_plain_text(data, indent=0):
    keys = sort_keys([str(key) for key in data.keys()])
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
        elif isinstance(value, dict):
            value = data_to_plain_text(value, indent=indent+2)
        lines.append(f"    \"{key}\": {value}".replace("'", '"'))
    spacer = "    " * indent
    return f"{{\n{spacer}" + f",\n{spacer}".join(lines) + f"\n{spacer}}}"


def plain_text_to_data(plain_text):
    return json.loads(plain_text)