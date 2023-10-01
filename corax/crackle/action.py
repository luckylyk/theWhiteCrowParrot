
from corax.crackle.parser import string_to_int_list, string_to_string_list


ACTION_KEYWORDS = [
    'aim', 'checkpoint', 'clear', 'disable', 'enable', 'fadein', 'fadeout',
    'flush', 'force', 'freeze', 'hide', 'join', 'init', 'layover', 'move',
    'pin', 'play', 'reach', 'restart', 'restore', 'run', 'start', 'stop',
    'show', 'set', 'shift', 'throw', 'unlock', 'wait']


def is_nolock_action(line):
    return line.startswith("nolock")


def has_subject(line):
    return line.split(" ")[0] not in ACTION_KEYWORDS


def filter_action(line):
    if not has_subject(line):
        return line.split(" ")[0]
    split = line.split(" ")
    if split[1] not in ACTION_KEYWORDS:
        raise SyntaxError("todo")
    return split[1]


def parse_reach_arguments(arguments):
    arguments = arguments.replace(" ", "").split(")by(")
    position = string_to_int_list(arguments[0])
    animations = string_to_string_list(arguments[-1])
    return position, animations


def parse_join_arguments(arguments):
    position, arguments = arguments.split(" from ")
    position = string_to_int_list(position)
    element, animations = arguments.split(" by ")
    animations = string_to_string_list(animations)
    return position, element, animations


def split_with_subject(line):
    split = line.split(" ")
    subject = split.pop(0)
    function = split.pop(0)
    arguments = " ".join(split)
    return subject, function, arguments
