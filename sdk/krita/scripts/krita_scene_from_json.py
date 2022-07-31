import json
import krita
import os
from PyQt5 import QtGui, QtCore


ROOT = r"D:\Works\code\GitHub\theWhiteCrowParrot\whitecrowparrot"
JSON = r"scenes\forest_01.json"


def remove_key_color(image):
    for i in range(image.width()):
        for j in range(image.height()):
            color = image.pixelColor(i, j)
            if color == QtGui.QColor(0, 255, 0, 255):
                image.setPixelColor(i, j, QtGui.QColor(0, 0, 0, 0))


def image_to_data(image):  # {{{
    return image.bits().asstring(image.width() * image.height() * 4)


jsonfile = os.path.join(ROOT, JSON)
with open(jsonfile, "r") as f:
    data = json.load(f)


soft = krita.Krita.instance()
document = soft.createDocument(
    data["boundary"][2],
    data["boundary"][3],
    data["name"],
    "RGBA",
    "U8",
    "",
    120.0)

soft.activeWindow().addView(document)
root = document.rootNode()
layer = None
for element in data["elements"]:
    if element["type"] == "layer":
        layer = document.createGroupLayer(element["name"])
        root.addChildNode(layer, None)
    elif element["type"] == "set_static":
        assert layer
        node = document.createNode(os.path.basename(element["name"]), "paintlayer")
        layer.addChildNode(node, None)
        image = QtGui.QImage(os.path.join(ROOT, "sets", element["file"]))
        remove_key_color(image)
        node.setPixelData(image_to_data(image), element['position'][0], element['position'][1], image.width(), image.height())

document.refreshProjection()