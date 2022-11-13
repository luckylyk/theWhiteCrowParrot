from PIL import Image
import sys

COLOR_SOURCES = (247, 242, 215, 255), (193, 189, 169, 255)
COLOR_TARGETS = (242, 160, 51, 255), (189, 124, 40, 255)
GREEN = (0, 255, 0, 255)

img = Image.open(
    "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot/"
    "animations/whitecrow/sword.png")
img = img.convert("RGBA")

pixdata = img.load()

# Clean the background noise, if color != white, then set to black.

for y in range(img.size[1]):
    for x in range(img.size[0]):
        if pixdata[x, y] == COLOR_SOURCES[0]:
            pixdata[x, y] = COLOR_TARGETS[0]
        elif pixdata[x, y] == COLOR_SOURCES[1]:
            pixdata[x, y] = COLOR_TARGETS[1]
        else:
            pixdata[x, y] = GREEN

img.save(
    "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot/"
    "animations/whitecrow/sword_honey.png")