
from corax.crackle.parser import string_to_int_list


ACTION_KEYWORDS = ["run", "play", "set", "wait", "freeze", "reach", "move", "force", "flush"]


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


def extract_reach_arguments(arguments):
    arguments = arguments.split(" ")
    position = string_to_int_list(arguments[0])
    animations = [a.strip(" ") for a in arguments[-1].strip("()").split(",")]
    return position, animations


def split_with_subject(line):
    split = line.split(" ")
    subject = split.pop(0)
    function = split.pop(0)
    arguments = " ".join(split)
    return subject, function, arguments
