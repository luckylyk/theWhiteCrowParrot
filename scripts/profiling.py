
import os

count = 0
paths = []
paths.append(os.path.join(os.path.dirname(__file__), "..", "corax"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "sdk", "pluck"))
# paths.append(os.path.join(os.path.dirname(__file__), "..", "sdk", "krita_scripts"))
paths.append(os.path.join(os.path.dirname(__file__), "..", "corax", "crackle"))
#paths.append(r"D:\Works\code\GitHub\pixtracy\pixtracy")
#paths.append(r"D:\Works\code\GitHub\ncachefactory\ncachefactory")

# paths.append(r"D:\Works\code\GitHub\montunolito\montunolito\core")
# paths.append(r"D:\Works\code\GitHub\hotbox_designer\hotbox_designer")
# paths.append(r"D:\Works\code\GitHub\hotbox_designer\hotbox_designer\designer")
# path = r"D:\Works\Python\GitHub\pixtracy\pixtracy"

filepaths = [os.path.join(p, f) for p in paths for f in os.listdir(p)]
for filepath in filepaths:
    if not filepath.endswith(".py"):
        continue
    with open(filepath, 'r') as f:
        for _ in f:
            count += 1
print("Total number of lines is:", count)