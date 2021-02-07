import os

count = 0
path = os.path.join(os.path.dirname(__file__), "..", "corax")
# path = r"D:\Works\Python\GitHub\ncachefactory\ncachefactory"
# path = r"D:\Works\Python\GitHub\hotbox_designer\hotbox_designer"
# path = r"D:\Works\Python\GitHub\hotbox_designer\hotbox_designer\designer"
# path = r"D:\Works\Python\GitHub\pixtracy\pixtracy"

for fname in os.listdir(path):
    if not fname.endswith(".py"):
        continue
    with open(os.path.join(path, fname), 'r') as f:
        for _ in f:
            count += 1
print("Total number of lines is:", count)