
import os
import corax.context as cctx
from pluck.data import DATA_TEMPLATES


def test_sheet_properties_valid(data):
    data_sanity_check(data, type_="spritesheet", keys_to_skip=["moves"])
    if data['default_move'] not in data['evaluation_order']:
        raise ValueError(f"{data['default_move']} not in {data['evaluation_order']}")
    for path in data['layers'].values():
        if not is_valid_animation_path(path):
            raise ValueError(f'No animation {path} found in Animation folder')


def is_valid_animation_path(path):
    fullpath = os.path.join(cctx.ANIMATION_FOLDER, path)
    return os.path.exists(fullpath)


def tree_sanity_check(tree):
    nodes = tree.flat()
    for node in nodes:
        if node.data is None:
            continue
        data_sanity_check(node.data)


def data_sanity_check(data, type_=None, keys_to_skip=None):
    assert isinstance(data, dict), "data as to be a dict"
    keys_to_skip = keys_to_skip or []
    type_ = type_ or data.get("type")
    assert type_ and type_ in DATA_TEMPLATES, f"{type_} is not a valid node type"
    template = DATA_TEMPLATES[type_]
    for key in template.keys():
        if key in keys_to_skip:
            continue
        assert key in data.keys(), f"Missing parameter: {key}"
    for key in data.keys():
        if key in keys_to_skip:
            continue
        assert key in template.keys(), f"Invalid parameter: {key}"
    for key, value in data.items():
        if value is None or key in keys_to_skip:
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

