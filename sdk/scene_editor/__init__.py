# generate environment
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
SDK_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)
sys.path.append(SDK_FOLDER)

# initialize project
import whitecrow.context as wctx
GAMEDATAS_FOLDER = os.path.join(MAIN_FOLDER, "data")
GAME_DATAS = wctx.initialize(GAMEDATAS_FOLDER)

from PyQt5 import QtWidgets, QtCore, QtGui
from whitecrow.core import ELEMENT_TYPES
from whitecrow.cordinates import Cordinates



GRAPHIC_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC, ELEMENT_TYPES.PLAYER
SET_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC


class SceneWidget(QtWidgets.QWidget):
    def __init__(self, scene_datas, block_size=None, parent=None):
        super().__init__(parent=parent)
        self.block_size = block_size
        self.scene_datas = scene_datas
        self.layers, self.elements = build_scene(self.scene_datas)
        w, h = scene_datas["boundary"][2], scene_datas["boundary"][3]
        self.setFixedSize(w, h)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            self.paint(painter)
            painter.end()
        except:
            raise

    def paint(self, painter):
        for element in self.elements:
            element.render(painter)
        render_grid(
            painter,
            self.rect(),
            self.block_size,
            self.scene_datas["grid_pixel_offset"])


def build_scene(scene_datas):
    layers = []
    elements = []
    layer = None
    for element in scene_datas["elements"]:
        if element["type"] == ELEMENT_TYPES.LAYER:
            if layer is not None:
                layers.append(layer)
            layer = element.copy()
            layer["elements"] = []
        if layer is None:
            raise ValueError("A scene muster start with a layer")
        if element["type"] not in SET_TYPES:
            continue # temporary skip until other elements types are implemented
        image = get_element_image(element)
        cordinates = get_element_cordinate(element)
        graphic_element = GraphicElement(
            image=image,
            cordinates=cordinates,
            element_type=element["type"],
            name=element.get("name", "unamed"))
        layer["elements"].append(graphic_element)
        elements.append(graphic_element)
    return layers, elements


def get_element_cordinate(element):

    if element["type"] in SET_TYPES:
        return  Cordinates(
            mirror=False,
            block_position=(0, 0),
            pixel_offset=element["position"])
    if element["type"] == ELEMENT_TYPES.PLAYER:
        raise NotImplementedError


def get_element_image(element):
    format_ = QtGui.QImage.Format_ARGB32_Premultiplied
    if element["type"] in SET_TYPES:
        path = os.path.join(wctx.SET_FOLDER, element["file"])
        image = QtGui.QImage(path)
        image2 = QtGui.QImage(image.size(), format_)
        w, h = image.size().width(), image.size().height()

    elif element["type"] == ELEMENT_TYPES.PLAYER:
        filepath = os.path.join(wctx.MOVE_FOLDER, element["movedatas_file"])
        with open(filepath, "r") as f:
            movedatas = json.load(f)
        img_path = os.path.join(wctx.ANIMATION_FOLDER, movedatas["filename"])
        w, h = movedatas["block_size"]
        image = QtGui.QImage(img_path)
        image2 = QtGui.QImage(QtCore.QSize(w, h), format_)
    # horrible fucking awfull scandalous ressource killing loop used
    # because that fucking basic "setAlphaChannel" method isn't available
    # in PyQt ): ): ): ): ): ): ):
    color = QtGui.QColor(255, 0, 0, 0)
    mask = image.createMaskFromColor(QtGui.QColor(*wctx.KEY_COLOR).rgb())
    for i in range(w):
        for j in range(h):
            if mask.pixelColor(i, j) == QtGui.QColor(255, 255, 255, 255):
                image2.setPixelColor(i, j, color)
                continue
            image2.setPixelColor(i, j, image.pixelColor(i, j))
    return image2


class GraphicElement():
    def __init__(self, image, cordinates, element_type, name):
        self.image = image
        self.name = name
        self.cordinates = cordinates
        self.type = element_type

    def render(self, painter):
        rect = QtCore.QRect(
            QtCore.QPoint(*self.cordinates.pixel_position),
            self.image.size())
        painter.drawImage(rect, self.image)


def render_grid(painter, rect, block_size, offset=None):
    x, y = offset or (0, 0)
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
    while x < rect.width():
        painter.drawLine(x, 0, x, rect.height())
        x += block_size
    while y < rect.width():
        painter.drawLine(0, y, rect.width(), y)
        y += block_size


for scene in GAME_DATAS["scenes"]:
    if scene["name"] == GAME_DATAS["start_scene"]:
        filename = scene["file"]
scene_filepath = os.path.join(wctx.SCENE_FOLDER, filename)
with open(scene_filepath, "r") as f:
    scene_datas = json.load(f)

import cProfile
app = QtWidgets.QApplication([])
scenewidget = SceneWidget(scene_datas, wctx.BLOCK_SIZE)

window = QtWidgets.QScrollArea()
window.setWidget(scenewidget)
window.show()
app.exec_()