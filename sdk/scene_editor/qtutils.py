
import os
import json

from PyQt5 import QtGui, QtCore

from corax.core import SOUND_TYPES, ELEMENT_TYPES
import corax.context as cctx
from scene_editor.datas import SET_TYPES, GRAPHIC_TYPES


HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
ICON_FOLDER = os.path.join(HERE, "icons")

ICON_MATCH = {
    SOUND_TYPES.SFX_COLLECTION: "sound_collection.png",
    SOUND_TYPES.SFX: "sound.png",
    SOUND_TYPES.MUSIC: "music.png",
    SOUND_TYPES.AMBIANCE: "ambiance.png",
    ELEMENT_TYPES.LAYER: "layer.png",
    ELEMENT_TYPES.PLAYER: "player.png",
    ELEMENT_TYPES.SET_STATIC: "set.png",
    ELEMENT_TYPES.SET_ANIMATED: "set.png",
    ELEMENT_TYPES.PARTICLES: "particles.png"
}


icons = {}


def get_icon(filename):
    if icons.get(filename) is None:
        icons[filename] = QtGui.QIcon(os.path.join(ICON_FOLDER, filename))
    return icons[filename]


def get_element_image(element):
    format_ = QtGui.QImage.Format_ARGB32_Premultiplied
    if element["type"] in SET_TYPES:
        path = os.path.join(cctx.SET_FOLDER, element["file"])
        image = QtGui.QImage(path)
        image2 = QtGui.QImage(image.size(), format_)
        w, h = image.size().width(), image.size().height()

    elif element["type"] == ELEMENT_TYPES.PLAYER:
        filepath = os.path.join(cctx.MOVE_FOLDER, element["movedatas_file"])
        with open(filepath, "r") as f:
            movedatas = json.load(f)
        img_path = os.path.join(cctx.ANIMATION_FOLDER, movedatas["filename"])
        w, h = movedatas["block_size"]
        image = QtGui.QImage(img_path)
        image2 = QtGui.QImage(QtCore.QSize(w, h), format_)
    # horrible fucking awfull scandalous ressource killing loop used
    # because that basic "setAlphaChannel" method isn't available
    # in PyQt5 ): ): ): ): ): ): ):
    color = QtGui.QColor(255, 0, 0, 0)
    mask = image.createMaskFromColor(QtGui.QColor(*cctx.KEY_COLOR).rgb())
    for i in range(w):
        for j in range(h):
            if mask.pixelColor(i, j) == QtGui.QColor(255, 255, 255, 255):
                image2.setPixelColor(i, j, color)
                continue
            image2.setPixelColor(i, j, image.pixelColor(i, j))
    return image2
