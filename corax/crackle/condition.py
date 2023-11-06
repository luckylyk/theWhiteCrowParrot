
from functools import partial

from corax.core import NODE_TYPES
from corax.crackle.collector import (
    property_collector, value_collector, item_collector, hitmap_collector)
from corax.crackle.parser import (
    object_attribute, object_name, object_type, BOOL_AS_STRING, string_to_bool,
    string_to_string_list)
from corax.hitmap import detect_hitmaps_collision
from corax.seeker import (
    find_animated_set, find_player, find_character, find_zone,
    find_plugin_shape)


def split_condition(line):
    result = line.split(" ")
    if len(result) > 3 and result[2].startswith("(") and result[-1].endswith(")"):
        # Check if the value is a valid list.
        result = result[:2] + [" ".join(result[2:])]
    if len(result) != 3:
        msg = f"{line}, {result}: syntax must be: Subject Operator Value"
        raise SyntaxError(msg)
    return result


def create_subject_value_collector(subject, theatre):
    subject_type = object_type(subject)
    match subject_type:
        case NODE_TYPES.PLAYER:
            seeker = find_player
            return create_animated_subject_collector(subject, seeker, theatre)
        case NODE_TYPES.NPC:
            seeker = find_character
            return create_animated_subject_collector(subject, seeker, theatre)
        case "gamepad":
            return create_gamepad_value_collector(subject, theatre)
        case "theatre":
            return create_theatre_value_collector(subject, theatre)
        case "zone":
            return create_zone_value_collector(subject, theatre)
        case "prop":
            seeker = find_animated_set
            return create_animated_subject_collector(
                subject, seeker, theatre.scene)


def create_zone_value_collector(subject, theatre):
    attribute = object_attribute(subject)
    zone = find_zone(theatre.scene, object_name(subject))
    if attribute == "enable":
        return property_collector(zone, [attribute])
    message = f"Zone collector for attribute {attribute} is not implemented."
    raise NotImplementedError(message)


def create_theatre_value_collector(subject, theatre):
    attribute = object_attribute(subject)
    if object_name(subject) == "scene" and attribute == "name":
        return property_collector(theatre, ['scene', 'name'])
    elif object_name(subject) == "globals":
        return item_collector(theatre.globals, attribute)


def create_gamepad_value_collector(subject, theatre):
    if object_name(subject) == "keys":
        attribute = object_attribute(subject)
        if attribute == "pressed":
            return theatre.input_buffer.pressed_delta
        elif attribute == "released":
            return theatre.input_buffer.released_delta
        elif attribute == "inputs":
            return theatre.input_buffer.inputs
        else:
            raise NameError(f"Unkown gamepad attribute: {attribute}")


def create_animated_subject_collector(subject, seeker, theatre):
    animated = seeker(theatre, object_name(subject))
    attribute = object_attribute(subject)
    match attribute.split('.')[0]:
        case "animation":
            properties = ['animation_controller', 'animation', 'name']
            return property_collector(animated, properties)
            # return lambda: animated.animation_controller.animation.name
        case "flip":
            properties = ['animation_controller', 'coordinate', 'flip']
            return property_collector(animated, properties)
        case "sheet":
            return property_collector(animated, ['sheet_name'])
        case "trigger":
            return property_collector(animated, ['trigger'])
        case "hitmap":
            name = attribute.split(".")[-1]
            return hitmap_collector(animated, name, animated.coordinate)
        case "visible":
            return property_collector(animated, ['visible'])


def create_plugin_value_collector(line, theatre):
    subject, command = [element.strip(' ') for element in line.split("get")]
    plugin_shape = find_plugin_shape(theatre.scene, object_name(subject))
    return partial(plugin_shape.collect_value, command)


def create_condition_checker(line, theatre):
    if line == "always":
        return value_collector(True)
    if line.startswith("plugin"):
        return create_plugin_value_collector(line, theatre)
    subject, comparator, value = split_condition(line)
    subject_collector = create_subject_value_collector(subject, theatre)
    if value in BOOL_AS_STRING:
        value = string_to_bool(value)
        vcollector = value_collector(value)
    elif value.startswith("("):
        value = string_to_string_list(value)
        vcollector = value_collector(value)
    elif '.hitmap.' in value:
        vcollector = create_subject_value_collector(value, theatre)
    else:
        vcollector = value_collector(value)
    collector = partial(
        check_condition,
        subject_collector,
        comparator,
        vcollector)
    if not callable(subject_collector):
        msg = f"Line can't create a valid subject collector: {line}"
        raise ValueError(msg)
    if not callable(vcollector):
        msg = f"Line can't create a valid value collector: {line}"
        raise ValueError(msg)
    return collector


def check_condition(subject_collector, comparator, value_collector):
    subject = subject_collector()
    value = value_collector()
    if comparator == "is":
        return subject == value
    if comparator == "is_not":
        return subject != value
    if comparator == "not_in":
        return subject not in value
    elif comparator == "has":
        return value in subject
    elif comparator == "in":
        return subject in value
    elif comparator == "overlaps":
        if all((subject, value)):
            return detect_hitmaps_collision(subject, value)
        return False
    raise NotImplementedError(f"Unknown comparator: \"{comparator}\"")
