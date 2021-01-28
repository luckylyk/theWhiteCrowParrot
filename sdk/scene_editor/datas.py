from corax.core import ELEMENT_TYPES, SOUND_TYPES


KEY_ORDER = "name", "type", "file", "position"
EXCLUDED_PROPERTIES = "sounds", "areas", "elements"
GRAPHIC_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC, ELEMENT_TYPES.PLAYER
SET_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC
SOUNDS_TYPES = (
    SOUND_TYPES.SFX_COLLECTION,
    SOUND_TYPES.SFX,
    SOUND_TYPES.MUSIC,
    SOUND_TYPES.AMBIANCE
)


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
    keys = sort_keys(list(map(str, data.keys())))
    lines = []
    for key in keys:
        value = data[key]
        if isinstance(value, str):
            value = f"\"{value}\""
        if isinstance(value, dict):
            value = data_to_plain_text(value, indent=indent+2)
        lines.append(f"    \"{key}\": {value}".replace("'", '"'))
    spacer = "    " * indent
    return f"{{\n{spacer}" + f",\n{spacer}".join(lines) + f"\n{spacer}}}"