import os

count = 0
path = os.path.join(os.path.dirname(__file__), "..", "whitecrow")
# path = r"D:\Works\Python\GitHub\ncachefactory\ncachefactory"
# path = r"D:\Works\Python\GitHub\hotbox_designer\hotbox_designer"
# path = r"D:\Works\Python\GitHub\hotbox_designer\hotbox_designer\designer"
# path = r"D:\Works\Python\GitHub\pixtracy\pixtracy"
fname = "test.txt"
for fname in os.listdir(path):
    if not fname.endswith(".py"):
        continue
    with open(os.path.join(path, fname), 'r') as f:
        for line in f:
            count += 1
print("Total number of lines is:", count)