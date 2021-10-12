
import os

count = 0
paths = [
    os.path.join(os.path.dirname(__file__), "..", "corax"),
    # os.path.join(os.path.dirname(__file__), "..", "sdk", "pluck"),
    # os.path.join(os.path.dirname(__file__), "..", "sdk", "krita_scripts"),
    os.path.join(os.path.dirname(__file__), "..", "corax", "crackle")]

# paths.append(os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "sheets"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "sheets/gamejam"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "scenes/gamejam"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "scripts"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot", "players"))

filepaths = [os.path.join(p, f) for p in paths for f in os.listdir(p)]
for filepath in filepaths:
    if not filepath.endswith(".py") and  not filepath.endswith(".json")  and  not filepath.endswith(".ckl") :
        continue
    with open(filepath, 'r') as f:
        for _ in f:
            count += 1
print("Total number of lines is:", count)