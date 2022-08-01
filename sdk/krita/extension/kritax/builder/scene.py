import json
import krita
import os
from PyQt5 import QtGui
from ..image import remove_key_color


def build_scene(root, filepath):
    jsonfile = f'{root}/{filepath}'
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
            image = QtGui.QImage(os.path.join(root, "sets", element["file"]))
            remove_key_color(image, QtGui.QColor(0, 255, 0, 255))
            data = image.bits().asstring(image.width() * image.height() * 4)
            node.setPixelData(
                data,
                element['position'][0],
                element['position'][1],
                image.width(),
                image.height())

    document.refreshProjection()