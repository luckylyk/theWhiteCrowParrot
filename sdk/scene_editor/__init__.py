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
import corax.context as cctx
GAMEDATAS_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_DATAS = cctx.initialize(GAMEDATAS_FOLDER)

from PyQt5 import QtWidgets, QtCore, QtGui
from corax.core import ELEMENT_TYPES, SOUND_TYPES
from corax.cordinates import Cordinates

from scene_editor.tree import create_scene_outliner_tree
from scene_editor.datas import SET_TYPES, GRAPHIC_TYPES, data_to_plain_text
from scene_editor.qtutils import get_element_image, ICON_FOLDER
from scene_editor.geometry import grow_rect, get_element_cordinate
from scene_editor.paint import (
    PaintContext, render_background, render_grid, render_sound)


class OutlinerView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)


class OutlinerTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(OutlinerTreeModel, self).__init__(parent)
        self._root = root

    def rowCount(self, parent):
        if not parent.isValid():
            return self._root.childCount()
        return parent.internalPointer().childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.name
        if role == QtCore.Qt.DecorationRole:
            return node.icon

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and section == 0:
            return "Scene"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        node = self.getNode(index)
        parent = node.parent()
        if parent == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def index(self, row, column, parent):
        parent = self.getNode(parent)
        child = parent.child(row)
        if not child:
            return QtCore.QModelIndex()
        return self.createIndex(row, column, child)

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root

    # def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
    #     parent_node = self.getNode(parent)
    #     self.beginInsertRows(parent, position, position + rows - 1)

    #     for _ in range(rows):
    #         childCount = parent_node.childCount()
    #         childNode = Node("untitled" + str(childCount))
    #         success = parent_node.insertChild(position, childNode)

    #     self.endInsertRows()
    #     return success

    # def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
    #     parent_node = self.getNode(parent)
    #     self.beginRemoveRows(parent, position, position + rows - 1)
    #     for _ in range(rows):
    #         success = parent_node.removeChild(position)
    #     self.endRemoveRows()
    #     return success


class SceneWidget(QtWidgets.QWidget):
    def __init__(
            self,
            scene_datas,
            block_size=None,
            paintcontext=None,
            parent=None):

        super().__init__(parent=parent)
        self.paintcontext = paintcontext or PaintContext(scene_datas)
        self.block_size = block_size
        self.scene_datas = scene_datas
        self.layers, self.elements = build_scene(self.scene_datas)
        self.recompute_size()

    def recompute_size(self):
        w, h = self.scene_datas["boundary"][2], self.scene_datas["boundary"][3]
        w = self.paintcontext.relatives(w) + (2 * self.paintcontext.extra_zone)
        h = self.paintcontext.relatives(h) + (2 * self.paintcontext.extra_zone)
        self.setFixedSize(w, h)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.recompute_size()
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            self.paint(painter)
            painter.end()
        except:
            raise

    def paint(self, painter):
        render_background(painter, self.rect(), self.paintcontext)
        for element in self.elements:
            element.render(painter, self.paintcontext)
        render_grid(
            painter,
            self.rect(),
            self.block_size,
            self.scene_datas["grid_pixel_offset"],
            self.paintcontext)
        for sound in self.scene_datas["sounds"]:
            render_sound(painter, sound, self.paintcontext)


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
        if element["type"] not in GRAPHIC_TYPES:
            continue # temporary skip until other elements types are implemented
        image = get_element_image(element)
        cordinates = get_element_cordinate(element, scene_datas["grid_pixel_offset"])
        graphic_element = GraphicElement(
            image=image,
            cordinates=cordinates,
            element_type=element["type"],
            name=element.get("name", "unamed"))
        layer["elements"].append(graphic_element)
        elements.append(graphic_element)
    return layers, elements


class GraphicElement():
    def __init__(self, image, cordinates, element_type, name):
        self.image = image
        self.name = name
        self.cordinates = cordinates
        self.type = element_type

    def render(self, painter, paintcontext):
        x = paintcontext.relatives(self.cordinates.pixel_position[0])
        y = paintcontext.relatives(self.cordinates.pixel_position[1])
        w = paintcontext.relatives(self.image.size().width())
        h = paintcontext.relatives(self.image.size().height())
        rect = QtCore.QRect(x, y, w, h)
        paintcontext.offset_rect(rect)
        painter.drawImage(rect, self.image)


if __name__ == "__main__":
    for scene in GAME_DATAS["scenes"]:
        if scene["name"] == GAME_DATAS["start_scene"]:
            filename = scene["file"]
    scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
    with open(scene_filepath, "r") as f:
        scene_datas = json.load(f)


    app = QtWidgets.QApplication([])
    # scenewidget = SceneWidget(scene_datas, cctx.BLOCK_SIZE)
    # window = QtWidgets.QScrollArea()
    # window.setWidget(scenewidget)
    # window.show()

    tree = create_scene_outliner_tree(scene_datas)
    model = OutlinerTreeModel(tree)
    view = OutlinerView()
    view.setModel(model)

    print([e.name for e in tree.flat()])

    def print_selection_data(selection, _):
        indexes = selection.indexes()
        data = model.getNode(indexes[0]).data
        if data is not None:
            print(data_to_plain_text(data))

    selection_model = view.selectionModel()
    selection_model.selectionChanged.connect(print_selection_data)


    view.show()


    stylesheetpath = os.path.join(os.path.dirname(__file__), "..", "flatdark.css")
    stylesheet = ""
    with open(stylesheetpath, "r") as f:
        for line in f:
            stylesheet += line

    app.setStyleSheet(stylesheet)

    app.exec_()