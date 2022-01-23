
from functools import partial
from corax.core import NODE_TYPES
from corax.seeker import find_animated_set, find_player
from corax.crackle.parser import (
    object_attribute, object_name, object_type, BOOL_AS_STRING, string_to_bool,
    string_to_string_list)


def split_condition(line):
    result = line.split(" ")
    if len(result) > 3 and result[2].startswith("(") and result[-1].endswith(")"):
        # check if the value is a valid list
        result = result[0:2] + [" ".join(result[2:])]
    if len(result) != 3:
        msg = f"{line}, {result}: syntax must be: Subject Operator Value"
        raise SyntaxError(msg)
    return result


def create_subject_value_collector(subject, theatre):
    subject_type = object_type(subject)
    if subject_type ==  NODE_TYPES.PLAYER:
        return create_player_subject_collector(subject, theatre)
    elif subject_type == "gamepad":
        return create_gamepad_value_collector(subject, theatre)
    elif subject_type == "theatre":
        return create_theatre_value_collector(subject, theatre)
    elif subject_type == "prop":
        return create_props_subject_collector(subject, theatre)


def create_theatre_value_collector(subject, theatre):
    attribute = object_attribute(subject)
    if object_name(subject) == "scene" and attribute == "name":
        return lambda: theatre.scene.name
    elif object_name(subject) == "globals":
        return lambda: theatre.globals[attribute]


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
            raise NameError("Unkown gamepad attribute: " + attribute)


def create_player_subject_collector(subject, theatre):
    player = find_player(theatre, object_name(subject))
    attribute = object_attribute(subject)
    if attribute == "animation":
        return lambda: player.animation_controller.animation.name
    elif attribute == "flip":
        return lambda: player.animation_controller.coordinate.flip
    elif attribute == "sheet":
        return lambda: player.sheet_name
    elif attribute.startswith("hitmap"):
        name = attribute.split(".")[-1]
        return lambda: player.animation.hitmaps[name]


def create_props_subject_collector(subject, theatre):
    props = find_animated_set(theatre.scene, object_name(subject))
    attribute = object_attribute(subject)
    if attribute == "animation":
        return lambda: props.animation_controller.animation.name


def create_condition_checker(line, theatre):
    if line == "always":
        return lambda: True
    subject, comparator, value = split_condition(line)
    subject_collector = create_subject_value_collector(subject, theatre)
    if value in BOOL_AS_STRING:
        value = string_to_bool(value)
    elif value.startswith("("):
        value = string_to_string_list(value)
    value_collector = lambda: value
    collector = partial(
        check_condition,
        subject_collector,
        comparator,
        value_collector)
    if not callable(subject_collector):
        msg = "Line can't create a valid subject collector: {}".format(line)
        raise ValueError(msg)
    if not callable(value_collector):
        msg = "Line can't create a valid value collector: {}".format(line)
        raise ValueError(msg)
    return collector


def check_condition(subject_collector, comparator, value_collector):
    subject = subject_collector()
    value = value_collector()
    if comparator == "is":
        return subject == value
    elif comparator == "has":
        return value in subject
    elif comparator == "in":
        return subject in value
    raise NotImplementedError(f"Comparator \"{comparator}\" is unknown")
