import json
import krita
import os
from PyQt5 import QtGui


ROOT = "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot"
JSON = "scenes/bearcave.json"


def remove_key_color(image):
    for i in range(image.width()):
        for j in range(image.height()):
            color = image.pixelColor(i, j)
            if color == QtGui.QColor(0, 255, 0, 255):
                image.setPixelColor(i, j, QtGui.QColor(0, 0, 0, 0))


def import_corax_scene(coraxroot, scenefile):
    with open(scenefile, "r") as f:
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
    scene_node = document.createGroupLayer(data["name"])
    root.addChildNode(scene_node, None)
    layer = None
    for element in data["elements"]:
        if element["type"] == "layer":
            layer = document.createGroupLayer(element["name"])
            scene_node.addChildNode(layer, None)
        elif element["type"] == "set_static":
            assert layer
            basename = os.path.basename(element["name"])
            node = document.createNode(basename, "paintlayer")
            layer.addChildNode(node, None)
            image = QtGui.QImage(os.path.join(ROOT, "sets", element["file"]))
            # Ensure Alpha channel exists (unless black replace transparent pixels)
            image = image.convertToFormat(QtGui.QImage.Format_ARGB32)
            remove_key_color(image)
            pixeldata = image.bits().asstring(image.width() * image.height() * 4)
            node.setPixelData(
                pixeldata,
                element['position'][0],
                element['position'][1],
                image.width(),
                image.height())
    document.refreshProjection()


if __name__ == "__main__":
    scenefile = f'{ROOT}/{JSON}'
    import_corax_scene(ROOT, scenefile)