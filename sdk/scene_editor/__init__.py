# generate environment
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
ICON_FOLDER = os.path.join(HERE, "icons")
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


GRAPHIC_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC, ELEMENT_TYPES.PLAYER
SET_TYPES = ELEMENT_TYPES.SET_ANIMATED, ELEMENT_TYPES.SET_STATIC
KEY_ORDER = "name", "type", "file", "position"
icons = {}


def get_icon(filename):
    if icons.get(filename) is None:
        icons[filename] = QtGui.QIcon(os.path.join(ICON_FOLDER, filename))
    return icons[filename]


def sort_keys(elements):
    copy = []
    for key in KEY_ORDER:
        if key in elements:
            copy.append(key)
            elements.remove(key)
    return copy + sorted(elements)


def data_to_plain_text(data, indent=0):
    keys = sort_keys(list(map(str, data.keys())))
    lines = []
    for key in keys:
        value = data[key]
        if isinstance(value, str):
            value = f"\"{value}\""
        if isinstance(value, dict):
            value = data_to_plain_text(value, indent=indent+2)
        lines.append(f"    \"{key}\": {value}".replace("'", '"'))
    spacer = "    " * indent
    return f"{{\n{spacer}" + f",\n{spacer}".join(lines) + f"\n{spacer}}}"


class PaintContext():
    def __init__(self, scene_datas):
        self.zoom = 1.5
        self._extra_zone = 200
        self.grid_color = "grey"
        self.grid_alpha = .2
        self.grid_border_color = "black"
        self.sound_zone_color = "blue"
        self.sound_fade_off = "red"
        self.background_color = "grey"
        self.level_background_color = scene_datas["background_color"]

    def relatives(self, value):
        return value * self.zoom

    def offset_rect(self, rect):
        rect.setLeft(rect.left() + self.extra_zone)
        rect.setTop(rect.top() + self.extra_zone)
        rect.setRight(rect.right() + self.extra_zone)
        rect.setBottom(rect.bottom() + self.extra_zone)

    @property
    def extra_zone(self):
        return self._extra_zone * self.zoom

    @extra_zone.setter
    def extra_zone(self, value):
        self._extra_zone = value

    def offset(self, x, y):
        x += self.extra_zone
        y += self.extra_zone
        return x, y

    def zoomin(self):
        self.zoom += self.zoom / 10
        self.zoom = min(self.zoom, 5)

    def zoomout(self):
        self.zoom -= self.zoom / 10
        self.zoom = max(self.zoom, .1)


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


class TreeNode():
    def __init__(self, name, icon, data=None, parent=None):
        self.name = name
        self.icon = icon
        self._parent = parent
        self.children = []
        self.data = data
        if parent is not None:
            self._parent.children.append(self)

    def childCount(self):
        return len(self.children)

    def parent(self):
        return self._parent

    def child(self, row):
        return self.children[row]

    def row(self):
        if self._parent is not None:
            return self._parent.children.index(self)


def create_scene_outliner_tree(scene_datas):
    root = TreeNode("scene", QtGui.QIcon())
    sounds = TreeNode("audios", get_icon("sound.png"), parent=root)

    for sound in scene_datas["sounds"]:
        if sound["type"] == SOUND_TYPES.SFX:
            icon = get_icon("sound.png")
        elif sound["type"] in SOUND_TYPES.SFX_COLLECTION:
            icon = get_icon("sound_collection.png")
        elif sound["type"] == SOUND_TYPES.MUSIC:
            icon = get_icon("music.png")
        else:
            icon = get_icon("particles.png")
        name = sound.get("name", "no name")
        TreeNode(name, icon, data=sound, parent=sounds)

    TreeNode("zones", get_icon("zone.png"), parent=root)

    renderable = TreeNode("renderable", get_icon("renderable.png"), parent=root)
    layer = None
    for element in scene_datas["elements"]:
        name = element.get("name", "no name")
        if element["type"] == ELEMENT_TYPES.LAYER:
            layer = TreeNode(name, get_icon("layer.png"), parent=renderable)
            continue
        elif element["type"] == ELEMENT_TYPES.PLAYER:
            icon = get_icon("player.png")
        elif element["type"] in SET_TYPES:
            icon = get_icon("set.png")
        elif element["type"] in ELEMENT_TYPES.PARTICLES:
            icon = get_icon("particles.png")
        else:
            icon = QtGui.QIcon()

        TreeNode(name, icon, data=element, parent=layer)

    return root


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


def grow_rect(rect, value):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() - value,
        rect.top() - value,
        rect.width() + (value * 2),
        rect.height() + (value * 2))


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


def get_element_cordinate(element, grid_offset=None):
    if element["type"] in SET_TYPES:
        return Cordinates(
            mirror=False,
            block_position=(0, 0),
            pixel_offset=element["position"])
    if element["type"] == ELEMENT_TYPES.PLAYER:
        return Cordinates(
            mirror=False,
            block_position=element["block_position"],
            pixel_offset=grid_offset)


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


def render_background(painter, rect, paintercontext):
    pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
    brush = QtGui.QBrush(QtGui.QColor(paintercontext.background_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)
    brush = QtGui.QBrush(QtGui.QColor(*paintercontext.level_background_color))
    painter.setBrush(brush)
    painter.drawRect(grow_rect(rect, -paintercontext.extra_zone))

    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    painter.setBrush(brush)


def render_sound(painter, sound, paintcontext=None):
    if sound["zone"] is None:
        return
    rect = QtCore.QRectF()
    rect.setLeft(paintcontext.relatives(sound["zone"][0]))
    rect.setTop(paintcontext.relatives(sound["zone"][1]))
    rect.setRight(paintcontext.relatives(sound["zone"][2]))
    rect.setBottom(paintcontext.relatives(sound["zone"][3]))
    paintcontext.offset_rect(rect)

    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    pen = QtGui.QPen(QtGui.QColor(paintcontext.sound_zone_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)

    falloff = paintcontext.relatives(sound["falloff"])
    rect = grow_rect(rect, -falloff)

    pen = QtGui.QPen(QtGui.QColor(paintcontext.sound_fade_off))
    pen.setStyle(QtCore.Qt.DashLine)
    painter.setPen(pen)
    painter.setBrush(brush)

    painter.drawRect(rect)

    image = QtGui.QImage(os.path.join(ICON_FOLDER, "sound.png"))
    l = rect.center().x() - (image.size().width() / 2)
    t = rect.center().y() - (image.size().height() / 2)
    point = QtCore.QPointF(l, t)
    painter.drawImage(point, image)


def render_grid(painter, rect, block_size, offset=None, paintcontext=None):
    rect = grow_rect(rect, -paintcontext.extra_zone)
    block_size = paintcontext.relatives(block_size)
    offset = offset or (0, 0)
    l = rect.left() + paintcontext.relatives(offset[0])
    t = rect.top() + paintcontext.relatives(offset[1])
    r = rect.right()
    b = rect.bottom()
    grid_color = QtGui.QColor(paintcontext.grid_color)
    grid_color.setAlphaF(paintcontext.grid_alpha)
    pen = QtGui.QPen(grid_color)
    painter.setPen(pen)
    x, y = l, t
    while x < r:
        painter.drawLine(x, t, x, b)
        x += block_size
    while y < b:
        painter.drawLine(l, y, r, y)
        y += block_size


    pen = QtGui.QPen(QtGui.QColor(paintcontext.grid_border_color))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.drawRect(rect)


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
view = QtWidgets.QTreeView()

view.setModel(model)

def print_selection_data(selection, _):
    indexes = selection.indexes()
    data = model.getNode(indexes[0]).data
    if data is not None:
        print(data_to_plain_text(data))

selection_model = view.selectionModel()
selection_model.selectionChanged.connect(print_selection_data)


view.show()

app.exec_()