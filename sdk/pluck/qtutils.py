
import os
import json

from PyQt5 import QtGui, QtCore, QtWidgets

from corax.core import NODE_TYPES
import corax.context as cctx
from corax.iterators import itertable
from pluck.data import SOUND_TYPES, ZONE_TYPES


HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
ICON_FOLDER = os.path.join(HERE, "icons")

ICON_MATCH = {
    NODE_TYPES.SFX_COLLECTION: "sound_collection.png",
    NODE_TYPES.SFX: "sound.png",
    NODE_TYPES.MUSIC: "music.png",
    NODE_TYPES.AMBIANCE: "ambiance.png",
    NODE_TYPES.NO_GO: "no_go.png",
    NODE_TYPES.INTERACTION: "interaction.png",
    NODE_TYPES.LAYER: "layer.png",
    NODE_TYPES.PLAYER: "player.png",
    NODE_TYPES.SET_STATIC: "set.png",
    NODE_TYPES.SET_ANIMATED: "set.png",
    NODE_TYPES.PARTICLES: "particles.png"
}


icons = {}
images = {}


def wait_cursor(func):
    def wrapper(*args, **kwargs):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        result = func(*args, **kwargs)
        QtWidgets.QApplication.restoreOverrideCursor()
        return result
    return wrapper


def set_shortcut(keysequence, parent, method):
    shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(keysequence), parent)
    shortcut.activated.connect(method)


def get_icon(filename):
    if icons.get(filename) is None:
        icons[filename] = QtGui.QIcon(os.path.join(ICON_FOLDER, filename))
    return icons[filename]


def key_color():
    return QtGui.QColor(*cctx.KEY_COLOR).rgb()


def get_image(element):
    if element is None:
        return
    filename = None
    if element["type"] in list(SOUND_TYPES) + list(ZONE_TYPES) + [NODE_TYPES.PLAYER]:
        filename = os.path.join(ICON_FOLDER, ICON_MATCH[element["type"]])
        if images.get(filename) is None:
            images[filename] = QtGui.QImage(filename)
    else:
        if element["type"] == NODE_TYPES.SET_STATIC:
            filename = os.path.join(cctx.SET_FOLDER, element["file"])
        if element["type"] == NODE_TYPES.SET_ANIMATED:
            filename = os.path.join(cctx.SHEET_FOLDER, element["file"])
        if filename is None:
            return
        if images.get(filename) is None:
            images[filename] = create_image(element)
    if filename is None:
        return None
    return images[filename]


def create_image(element):
    if element["type"] == NODE_TYPES.SET_STATIC:
        path = os.path.join(cctx.SET_FOLDER, element["file"])
        image = QtGui.QImage(path)
        size = image.size().width(), image.size().height()
        return merge_images([image], size)

    elif element["type"] != NODE_TYPES.SET_ANIMATED:
        raise ValueError(element["type"] + " is not supported")

    folder = element.get("sheetdata_file", element.get("file"))
    filepath = os.path.join(cctx.SHEET_FOLDER, folder)

    with open(filepath, "r") as f:
        movedata = json.load(f)

    filenames = [v for _, v in movedata["layers"].items()]
    paths = [os.path.join(cctx.ANIMATION_FOLDER, fn) for fn in filenames]
    size = movedata["frame_size"]
    images = [QtGui.QImage(path) for path in paths]
    return merge_images(images, size)


def merge_images(images, size):
    # horrible fucking awfull scandalous ressource killing loop used
    # because that basic "setAlphaChannel" method isn't available
    # in PyQt5 ): ): ): ): ): ): ):
    format_ = QtGui.QImage.Format_ARGB32_Premultiplied
    result = QtGui.QImage(images[0].size(), format_)
    green = key_color()
    transparent = QtGui.QColor(0, 0, 0, 0)
    for i, j in itertable(*size):
        if all(image.pixelColor(i, j).rgb() == green for image in images):
            result.setPixelColor(i, j, transparent)
            continue
        for image in images:
            if image.pixelColor(i, j) != green:
                result.setPixelColor(i, j, image.pixelColor(i, j))
    return result


def get_spritesheet_image_from_index(filename, index):
    path = os.path.join(cctx.SHEET_FOLDER, filename)
    with open(path, "r") as f:
        data = json.load(f)
    filename = os.path.join(cctx.ANIMATION_FOLDER, data["filename"])
    return spritesheet_to_images(filename, data["frame_size"])[index]


def build_spritesheet_image(filenames):
    images = [QtGui.QImage(filename) for filename in filenames]
    size = images[0].size().width(), images[0].size().height()
    return merge_images(images, size)


def spritesheet_to_images(filenames, frame_size):
    sheet = build_spritesheet_image(filenames)
    width, height = frame_size
    row = sheet.height() / height
    col = sheet.width() / width
    images = []
    for j, i in itertable(int(row), int(col)):
        x, y = i * width, j * height
        image = sheet.copy(x, y, width, height)
        images.append(image)
    return images


def sub_rects(rect, size):
    width, height = size
    row = rect.height() / height
    col = rect.width() / width
    rects = []
    for j, i in itertable(int(row), int(col)):
        x, y = i * width, j * height
        rects.append(QtCore.QRectF(x, y, width, height))
    return rects
