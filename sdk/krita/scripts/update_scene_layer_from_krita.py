import shutil
import json
import krita
import os
from PyQt5 import QtGui, QtCore


SRGB_PROFILE = "sRGB-elle-V2-srgbtrc.icc"
ROOT = "D:/Works/code/GitHub/theWhiteCrowParrot/whitecrowparrot"
SET_ROOT = f'{ROOT}/sets'
BACKUP_ROOT = f'{ROOT}/setbackup'
JSON = "scenes/honeywarehouse_cave.json"


def load_scene(coraxroot, scenefile):
    filepath = f'{coraxroot}/{scenefile}'
    backup = f'{coraxroot}/{scenefile}_backup'
    shutil.copy(filepath, backup)
    with open(filepath, "r") as f:
        return json.load(f)


def node_bounds(node, document):
    rect = node.bounds()
    width, height = document.width(), document.height()
    rect.setLeft(max(rect.left(), 0))
    rect.setTop(max(rect.top(), 0))
    rect.setRight(rect.right() if rect.right() <= width else width)
    rect.setBottom(rect.bottom() if rect.bottom() <= height else height)
    return rect.x(), rect.y(), rect.width(), rect.height()


def node_to_qimage(node, document):
    """
    Returns an QImage 8-bit sRGB
    """
    x, y, w, h = node_bounds(node, document)

    canvas = QtGui.QImage(QtCore.QSize(w, h), QtGui.QImage.Format_ARGB32)
    canvas.fill(QtGui.QColor(0, 255, 0))

    is_srgb = (
        node.colorModel() == "RGBA" and
        node.colorDepth() == "U8" and
        node.colorProfile().lower() == SRGB_PROFILE.lower())

    if is_srgb:
        pixel_data = node.projectionPixelData(x, y, w, h).data()
    else:
        temp_node = node.duplicate()
        temp_node.setColorSpace("RGBA", "U8", SRGB_PROFILE)
        pixel_data = temp_node.projectionPixelData(x, y, w, h).data()

    image = QtGui.QImage(pixel_data, w, h, QtGui.QImage.Format_ARGB32)
    painter = QtGui.QPainter(canvas)
    painter.drawImage(0, 0, image)

    return canvas

if not os.path.exists(BACKUP_ROOT):
    os.makedirs(BACKUP_ROOT)

soft = krita.Krita()
document = soft.activeDocument()
nodes = document.activeNode().childNodes()
data = load_scene(ROOT, JSON)

for node in nodes:
    if not node.visible():
        continue
    for element in data['elements']:
        if element['name'] != node.name():
            continue
        filepath = f'{SET_ROOT}/{element["file"]}'
        backup = f'{BACKUP_ROOT}/{element["file"]}'
        if not os.path.exists(os.path.dirname(backup)):
            os.makedirs(os.path.dirname(backup))
        shutil.copy(filepath, backup)
        image = node_to_qimage(node, document)
        image.save(filepath, "PNG")
        element["position"] = node_bounds(node, document)[:2]
        print("update ->", element["name"], "save:", filepath, "backup", backup)


with open(f'{ROOT}/{JSON}', "w") as f:
    json.dump(data, f , indent=4)
