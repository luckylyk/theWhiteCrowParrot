"""
This is a debug system.
If an override json is set as argument at the Corax Engine start, the values
the original values will be overrided by the one contained in the override file.
This allow to test some part of the game, whitout having to start from scatch
each time and in the meantime, it avoids to edit the game data to start with
another change.
"""

from functools import reduce
import json
import logging
from operator import getitem
import os
import re

import corax.context as cctx

OVERRIDE_MSG = "Override set value {2} for keys {1} in file {0}"
overrides_data = None

KEY_PATTERN = re.compile(r"(?<=\[).+?(?=\])")
RESULT_PATTERN = re.compile(r"\=(.*)")
FILENAME_PATTERN = re.compile(r"^(.*?)\[.*")


def type_value(value):
    value = value.strip(" ")
    if value.startswith('"'):
        return value.strip('"')
    elif value == "true":
        return True
    elif value == "false":
        return False
    elif int(value) == float(value):
        return int(value)
    return float(value)


def extract_line_infos(line):
    filename = FILENAME_PATTERN.findall(line)[0]
    keys = [type_value(k) for k in KEY_PATTERN.findall(line)]
    value = type_value(RESULT_PATTERN.findall(line)[0])
    return filename, keys, value


def parse_override_file(path):
    result = {}
    with open(path, 'r') as f:
        for line in f:
            filename, keys, value = extract_line_infos(line)
            result.setdefault(filename, [])
            result[filename].append([keys, value])
    return result


def load_json(filename):
    """
    This intermediate function to load a json file is looking for existing
    overrided keys and replace them in the result.
    """

    with open(filename, 'r') as f:
        data = json.load(f)

    if not cctx.OVERRIDE_FILE:
        return data

    global overrides
    if not overrides_data:
        with open(cctx.OVERRIDE_FILE, 'r') as f:
            overrides = parse_override_file(cctx.OVERRIDE_FILE)

    for file_, overrides in overrides.items():
        key_path = os.path.join(cctx.ROOT, file_)
        if os.path.normpath(key_path) != os.path.normpath(filename):
            continue
        for keys, value in overrides:
            *first_keys, last_key = keys
            reduce(getitem, first_keys, data)[last_key] = value
            msg = OVERRIDE_MSG.format(file_, [str(k) for k in keys], value)
            logging.info(msg)

    return data
