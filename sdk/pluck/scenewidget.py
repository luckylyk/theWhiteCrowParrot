
# generate environment
import os
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
SDK_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)
sys.path.append(SDK_FOLDER)

from PySide6 import QtWidgets, QtGui, QtCore


import corax.context as cctx
from corax.core import NODE_TYPES
from pluck.paint import PaintContext, render_grid, render_sound
from pluck.qtutils import set_shortcut, get_image
from pluck.ressource import load_json
from pluck.tree import list_layers, create_scene_outliner_tree


def tree_rect(tree):
    nodes = [
        n for l in list_layers(tree)
        for n in l.flat()
        if l.has_to_be_rendered and
        n.data.get("position")]

    x, y, r, b = 0, 0, 0, 0
    for node in nodes:
        image = get_image(node.data)
        if not image:
            continue
        x = min(x, node.data['position'][0])
        y = min(y, node.data['position'][1])
        r = max(r, node.data['position'][0] + image.width())
        b = max(b, node.data['position'][1] + image.height())
    rect = QtCore.QRect()
    rect.setTopLeft(QtCore.QPoint(x, y))
    rect.setBottomRight(QtCore.QPoint(r, b))
    return rect


class SceneWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mode_manager = ModeManager()
        self.paintcontext = PaintContext()
        self.paintcontext.extra_zone = 0
        self.setMouseTracking(True)
        self.tree = None

        set_shortcut("F", self, self.reset)

    def set_tree(self, tree):
        self.tree = tree
        self.reset()
        self.repaint()

    def reset(self):
        self.paintcontext.reset()
        tree_rect_ = tree_rect(self.tree)
        self.paintcontext.center = [
            self.rect().center().x()-tree_rect_.center().x(),
            self.rect().center().y() - tree_rect_.center().y()]
        self.repaint()

    def resizeEvent(self, event):
        size = (event.size() - event.oldSize()) / 2
        self.paintcontext.center[0] += size.width()
        self.paintcontext.center[1] += size.height()
        self.repaint()

    def mousePressEvent(self, event):
        self.mode_manager.update(event, pressed=True)

    def mouseReleaseEvent(self, event):
        self.mode_manager.update(event, pressed=False)

    def keyPressEvent(self, event):
        self.mode_manager.update(event, pressed=True)

    def keyReleaseEvent(self, event):
        self.mode_manager.update(event, pressed=False)

    def wheelEvent(self, event):
        # To center the zoom on the mouse, we save a reference mouse position
        # and compare the offset after zoom computation.
        abspoint = self.paintcontext.absolute_point(event.position())
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        relcursor = self.paintcontext.relative_point(abspoint)
        vector = relcursor - event.position()
        center = self.paintcontext.center
        result = [center[0] - vector.x(), center[1] - vector.y()]
        self.paintcontext.center= result
        self.repaint()

    def mouseMoveEvent(self, event):
        match self.mode_manager.mode:
            case ModeManager.SELECTION:
                return
            case ModeManager.NAVIGATION:
                offset = self.mode_manager.mouse_offset(event.position())
                if offset is not None:
                    x = self.paintcontext.center[0] + offset.x()
                    y = self.paintcontext.center[1] + offset.y()
                    self.paintcontext.center = [x, y]
        self.repaint()

    def offset(self, point):
        return self.rect().center() + point.toPoint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        if not self.tree:
            return

        nodes = [
            n for l in list_layers(self.tree)
            for n in l.flat() if l.has_to_be_rendered]

        for node in nodes:
            if not node.visible:
                continue
            match node.data.get("type"):
                case NODE_TYPES.SET_STATIC:
                    image = get_image(node.data)
                    if not image:
                        continue
                    x, y = node.data['position']
                    w, h = image.width(), image.height()
                    rect = QtCore.QRect(x, y, w, h)
                    rect = self.paintcontext.relatives_rect(rect)
                    painter.drawImage(rect, image)

        for node in self.tree.children[0].children[0].children:
            if not node.data['zone']:
                continue
            zone = node.data['zone']
            rect = QtCore.QRect()
            rect.setTopLeft(QtCore.QPoint(zone[0], zone[1]))
            rect.setBottomRight(QtCore.QPoint(zone[2], zone[3]))
            rect = self.paintcontext.relatives_rect(rect)
            image = get_image(node.data)
            render_sound(painter, node.data, rect, image, self.paintcontext)

        render_grid(
            painter,
            self.rect(),
            cctx.BLOCK_SIZE,
            self.paintcontext)

        painter.end()


class ModeManager:
    SELECTION = 'selection'
    NAVIGATION = 'navigation'

    def __init__(self):
        self.left_click_pressed = False
        self.mouse_ghost = None
        self.keys_pressed = set()
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False

    def update(self, event, pressed=False):
        if isinstance(event, QtGui.QMouseEvent):
            self.update_mouse(event, pressed)
        elif isinstance(event, QtGui.QKeyEvent):
            self.update_keys(event, pressed)

    def update_mouse(self, event, pressed):
        match event.button():
            case QtCore.Qt.LeftButton:
                self.left_click_pressed = pressed
            case QtCore.Qt.RightButton:
                self.right_click_pressed = pressed

    def update_keys(self, event, pressed):
        if pressed is True:
            self.keys_pressed.add(event.key())
        elif event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())

    @property
    def mode(self):
        space = QtCore.Qt.Key_Space
        if self.left_click_pressed is True and space in self.keys_pressed:
            return ModeManager.NAVIGATION
        self.mouse_ghost = None
        return ModeManager.SELECTION

    def mouse_offset(self, position):
        result = position - self.mouse_ghost if self.mouse_ghost else None
        self.mouse_ghost = position
        return result.toPoint() if result else None


if __name__ == "__main__":

# initialize project
    import corax.context as cctx
    GAMEDATA_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")

    class MockArguments:
        """
        The Corax Engine uses an argparse object to initialize. This is a argparse
        mocker to be able to initialize the engine for sdk uses.
        """
        game_root = GAMEDATA_FOLDER
        debug = False
        mute = True
        speedup = False
        overrides = None


    GAME_DATA = cctx.initialize(MockArguments)
    app = QtWidgets.QApplication()
    wid = SceneWidget()
    path = r"D:\Works\code\GitHub\theWhiteCrowParrot\whitecrowparrot\scenes\forest_01.json"
    tree = create_scene_outliner_tree(load_json(path))
    # print(tree)
    wid.show()
    wid.set_tree(tree)
    app.exec()