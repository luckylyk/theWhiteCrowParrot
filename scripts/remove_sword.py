import sys
import itertools
from PIL import Image

REMOVE = False
SWORD_COLORS = (150, 161, 170, 255), (43, 54, 62, 255)
GREEN = (0, 255, 0, 255)

file = (
    "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot/"
    "animations/whitecrow/exploration_sword.png")
img = Image.open(file)
img = img.convert("RGBA")

pixdata = img.load()

# Clean the background noise, if color != white, then set to black.

for y, x in itertools.product(range(img.size[1]), range(img.size[0])):
    if REMOVE:
        if pixdata[x, y] in SWORD_COLORS:
            pixdata[x, y] = GREEN
    else:
        if pixdata[x, y] not in SWORD_COLORS:
            pixdata[x, y] = GREEN

img.save(file)