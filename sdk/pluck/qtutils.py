
import os
import json
import numpy as np

from PIL import Image, ImageQt

from PySide6 import QtGui, QtCore, QtWidgets
from corax.core import NODE_TYPES
import corax.context as cctx
from corax.iterators import itertable
from pluck.data import SOUND_TYPES, ZONE_TYPES


HERE = os.path.dirname(os.path.realpath(__file__))
ICON_FOLDER = os.path.join(HERE, "icons")

ICON_MATCH = {
    NODE_TYPES.AMBIANCE: "ambiance.png",
    NODE_TYPES.COLLIDER: "collision.png",
    NODE_TYPES.EVENT_ZONE: "interaction.png",
    NODE_TYPES.INTERACTION: "interaction.png",
    NODE_TYPES.LAYER: "layer.png",
    NODE_TYPES.PLAYER: "player.png",
    NODE_TYPES.MUSIC: "music.png",
    NODE_TYPES.NPC: "player.png",
    NODE_TYPES.NO_GO: "no_go.png",
    NODE_TYPES.PARTICLES: "particles.png",
    NODE_TYPES.RELATIONSHIP: "interaction.png",
    NODE_TYPES.SET_STATIC: "set.png",
    NODE_TYPES.SET_ANIMATED: "set.png",
    NODE_TYPES.SFX_COLLECTION: "sound_collection.png",
    NODE_TYPES.SFX: "sound.png",
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
    shortcut = QtGui.QShortcut(QtGui.QKeySequence(keysequence), parent)
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
    types = (
        list(SOUND_TYPES) +
        list(ZONE_TYPES) +
        [NODE_TYPES.PLAYER,
        NODE_TYPES.NPC])
    if element["type"] in types:
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
        return remove_key_color(path)

    elif element["type"] != NODE_TYPES.SET_ANIMATED:
        raise ValueError(element["type"] + " is not supported")

    folder = element.get("sheetdata_file", element.get("file"))
    filepath = os.path.join(cctx.SHEET_FOLDER, folder)

    with open(filepath, "r") as f:
        movedata = json.load(f)

    filenames = [v for _, v in movedata["layers"].items()]
    paths = [os.path.join(cctx.ANIMATION_FOLDER, fn) for fn in filenames]
    size = movedata["frame_size"]
    image = build_spritesheet_image(paths)
    return spritesheet_to_images(image, size)[0]


def remove_key_color(filename):
    orig_color = tuple(cctx.KEY_COLOR + [255])
    replacement_color = (0, 0, 0, 0)
    image = Image.open(filename).convert('RGBA')
    data = np.array(image)
    data[(data == orig_color).all(axis = -1)] = replacement_color
    return ImageQt.ImageQt(Image.fromarray(data, mode='RGBA'))


def build_spritesheet_image(filenames):
    if not filenames:
        return
    orig_color = tuple(cctx.KEY_COLOR + [255])
    replacement_color = (0, 0, 0, 0)
    images = []
    for filename in filenames:
        image = Image.open(filename).convert('RGBA')
        data = np.array(image)
        data[(data == orig_color).all(axis = -1)] = replacement_color
        images.append(Image.fromarray(data, mode='RGBA'))

    background, *images = images
    for image in images:
        background.paste(image, (0, 0, image.size[0], image.size[1]), image)

    return ImageQt.ImageQt(background)


def spritesheet_to_images(sheet, frame_size):
    if not sheet:
        return []
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
