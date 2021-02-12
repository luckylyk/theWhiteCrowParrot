"""
This module contains all function used to read crackle script files.
The cackle language is the language read by the corax engine to drive scripted
event and story script.
"""


import os
import corax.context as cctx
from corax.crackle.script import CrackleScript


def load_scripts():
    """
    Load all scripts located in the folder <root>/scripts
    It parse the crackle files and build CrackleScript objects from.
    """
    scripts = []
    for filename in os.listdir(cctx.SCRIPT_FOLDER):
        filepath = os.path.join(cctx.SCRIPT_FOLDER, filename)
        namespace = ".".join(filename.split(".")[:-1])
        scripts.extend(parse_crackle_file(filepath, namespace))
    return scripts


def parse_crackle_file(filepath, namespace):
    """
    Parse a crackle file and convert it to CrackleScript object
    """
    scripts = []
    indent_level = 0
    with open(filepath) as f:
        script = None
        for i, line in enumerate(f):
            line = remove_commentaries(line)
            line = line.rstrip(" \n")
            if line.strip(" ") == "":
                pass
            elif line.startswith("script"):
                if script is not None:
                    scripts.append(script)
                name = f"{namespace}.{extract_script_name(line)}"
                script = CrackleScript(name)
                indent_level = 1
            elif script is None:
                msg = "file must start by a script definition"
                raise SyntaxError(f"line {i} > invalid stucture > {msg}")
            elif line.startswith("        "):
                script.actions.append(line.strip(" "))
                indent_level = 2
            elif line.startswith("    "):
                if indent_level == 2:
                    msg = "conditions must be set before actions"
                    raise SyntaxError(f"line {i} > invalid indent > {msg}")
                script.conditions.append(line.strip(" "))
            else:
                msg = "unrecongnized indent"
                raise SyntaxError(f"line {i} > unknown > {msg}")
        scripts.append(script)
    return scripts


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



