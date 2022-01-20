"""
This module contains all function used to read crackle script files.
The cackle language is the language read by the corax engine to drive scripted
event and story script.
"""


import os
import corax.context as cctx
from corax.crackle.script import CrackleEvent, CrackleScript


FUNCTION_TYPES = "script", "event"


def load_scripts(theatre):
    """
    Load all scripts located in the folder <root>/scripts
    It parse the crackle files and build CrackleScript objects from.
    """
    scripts = []
    for filename in os.listdir(cctx.SCRIPT_FOLDER):
        filepath = os.path.join(cctx.SCRIPT_FOLDER, filename)
        namespace = ".".join(filename.split(".")[:-1])
        scripts.extend(parse_crackle_file(filepath, namespace))
    # OUCH, afterward, that bi-directionnal connection create a mess and could
    # lead to impossible debug. That should get a better design.
    for script in scripts:
        script.theatre = theatre
    return scripts


def parse_crackle_file(filepath, namespace):
    """
    Parse a crackle file and convert it to CrackleScript object
    """
    scripts = []
    events = []
    i = 0
    line = ""
    with open(filepath, "r") as f:
        while True:
            if line is None:
                break
            if not line:
                line = next_line(f)
                i += 1
            elif line.startswith("script"):
                name = f"{namespace}.{extract_script_name(line)}"
                script, i, line = build_script(f, i, name)
                scripts.append(script)
            elif line.startswith("event"):
                name = f"{namespace}.{extract_script_name(line)}"
                event, i, line = build_event(f, i, name)
                events.append(event)
            else:
                msg = f"line {i} > Unrecognized line > {namespace}"
                raise SyntaxError(msg)
    return scripts, events


def build_event(f, i, name):
    event = CrackleEvent(name)
    while True:
        try:
            line = next_line(f)
            i += 1
            if not line:
                continue
        except StopIteration:
            return event, i, None

        if line.split(" ")[0] in FUNCTION_TYPES:
            return event, i, line

        elif line.startswith("     ") or not line.startswith("    "):
            msg = (
                "each event action has to start with one "
                "indent level (4 spaces)")
            raise SyntaxError(f"line {i} > invalid indent > {msg}")

        event.actions.append(line.strip(" "))


def build_script(f, i, name):
    script = CrackleScript(name)
    indent_level = 1
    while True:
        try:
            line = next_line(f)
            i += 1
            if not line:
                continue
        except StopIteration:
            return script, i, None

        if line.startswith("        "):
            script.actions.append(line.strip(" "))
            indent_level = 2

        elif line.startswith("    "):
            if indent_level == 2:
                msg = "conditions must be set before actions"
                raise SyntaxError(f"line {i} > invalid indent > {msg}")
            script.conditions.append(line.strip(" "))

        elif line.split(" ")[0] in FUNCTION_TYPES:
            return script, i, line

        else:
            raise SyntaxError(f'line {i} > unknown > unrecongnized indent')


def next_line(f):
    line = next(f)
    line = remove_commentaries(line)
    return line.rstrip(" \n")


def remove_commentaries(line):
    if "//" not in line:
        return line
    elif line.strip(" ").startswith("//"):
        return ""
    return line.split("//")[0]


def extract_script_name(line):
    elements = line.split(" ")
    if len(elements) != 2:
        raise SyntaxError(
            "script definition must be 'script name'\n"
            "space are not allowed in script name")
    return elements[-1]



