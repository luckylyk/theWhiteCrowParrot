import json
import krita
import os
from PyQt5 import QtGui, QtCore


ROOT = r"D:\Works\code\GitHub\theWhiteCrowParrot\whitecrowparrot"
JSON = r"scenes\forest_01.json"


def pillow_to_qbytearray(image):
    for i in range(image.width()):
        for j in range(image.height()):
            color = image.pixelColor(i, j)
            if color == QtGui.QColor(0, 255, 0, 255):
                image.setPixelColor(i, j, QtGui.QColor(0, 0, 0, 0))
    return image_to_data(image)


def image_to_data(image):  # {{{
    ba = QtCore.QByteArray()
    buf = QtCore.QBuffer(ba)
    buf.open(QtCore.QBuffer.WriteOnly)
    ret = bytes(ba.data())
    buf.close()
    return ret


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
        data = pillow_to_qbytearray(image)
        node.setPixelData(pillow_to_qbytearray(), 0, 0, image.width(), image.height())
document.refreshProjection()