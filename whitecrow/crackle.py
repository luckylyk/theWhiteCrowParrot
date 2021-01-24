import os
import whitecrow.context as wctx


class CrackleScript:
    def __init__(self, name):
        self.name = name
        self.conditions = []
        self.actions = []

    def __str__(self):
        lines = self.conditions + self.actions
        return f"script {self.name}\n" + "\n".join(lines)


def read_crackle_file(filepath):
    scripts = []
    indent_level = 0
    with open(os.path.join(wctx.SCRIPT_FOLDER, filepath)) as f:
        script = None
        for i, line in enumerate(f):
            line = remove_commentaries(line)
            line = line.rstrip(" \n")
            if line.strip(" ") == '':
                pass
            elif line.startswith("script"):
                if script is not None:
                    scripts.append(script)
                script = CrackleScript(extract_script_name(line))
                indent_level = 1
            elif script is None:
                msg = "file must start by a script definition"
                raise SyntaxError(f"line {i} > invalid stucture > {msg}")
            elif line.startswith("        "):
                script.actions.append(line)
                indent_level = 2
            elif line.startswith("    "):
                if indent_level == 2:
                    msg = "conditions must be set before actions"
                    raise SyntaxError(f"line {i} > invalid indent > {msg}")
                script.conditions.append(line)
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