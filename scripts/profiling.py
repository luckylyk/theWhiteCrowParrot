
import os

count = 0
paths = [
    os.path.join(os.path.dirname(__file__), "..", "corax"),
    os.path.join(os.path.dirname(__file__), "..", "corax", "crackle"),
    os.path.join(os.path.dirname(__file__), "..", "sdk", "pluck"),
    os.path.join(os.path.dirname(__file__), "..", "sdk", "conus"),
    os.path.join(os.path.dirname(__file__), "..", "sdk", "krita", "scripts"),
    # os.path.join(os.path.dirname(__file__), "..", "sdk", "krita", "extensions"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "sheets"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "scenes"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "scripts"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "characters"),
    os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "relationships")
]


filepaths = [os.path.join(p, f) for p in paths for f in os.listdir(p)]
imports = set()
for filepath in filepaths:
    if not filepath.endswith(".py") and not filepath.endswith(".json") and not filepath.endswith(".ckl") :
        continue
    with open(filepath, 'r') as f:
        for line in f:
            count += 1
            if filepath.endswith(".py"):
                conditions = (
                    ("import " in str(line) or str(line).startswith("from ")) and
                    "corax" not in str(line) and "corax" not in str(line))
                if conditions:
                    imports.add(line.strip(" "))


print("Total number of lines is:", count)
print("-------------------------")
print("".join(sorted(list(imports))))