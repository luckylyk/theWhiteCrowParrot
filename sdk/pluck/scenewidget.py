
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
from corax.coordinate import to_block_position

from pluck.geometry import status_bar_rects, status_thumbnail_rect, get_node_rect
from pluck.paint import (
    PaintContext, render_grid, render_sound, render_selection_square,
    render_scenewidget_status_bar, render_zone, render_boundaries,
    render_background)
from pluck.qtutils import set_shortcut, get_image
from pluck.ressource import load_json
from pluck.tree import (
    list_layers, create_scene_outliner_tree, clear_tree_selection)


def hovered_nodes(nodes, position, paintcontext):
    return [
        node for node in nodes
        if (rect:=get_node_rect(node, paintcontext))
        and rect.contains(position)]


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
    nodeSelected = QtCore.Signal(object)
    zoneSelected = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mode_manager = ModeManager()
        self.highlighter = NodeHighligther()
        self.paintcontext = PaintContext()
        self.paintcontext.extra_zone = 0
        self.setMouseTracking(True)
        self.tree = None
        self.data = None
        self.grid = True
        self.boundaries = True
        self.is_exploring = False
        self.selection_square = SelectionSquare(self.paintcontext)
        self.zone_square = ZoneSquare(self.paintcontext)

        self.sizeHint = lambda: QtCore.QSize(1200, 800)
        self.backed_focus = None
        set_shortcut("F", self, self.reset)

    def set_tree(self, tree):
        self.tree = tree
        self.selection_square.tree = tree
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

    def enterEvent(self, _):
        self.backed_focus = QtWidgets.QApplication.focusWidget()
        self.setFocus(QtCore.Qt.MouseFocusReason)
        return

    def leaveEvent(self, _):
        if self.backed_focus:
            self.backed_focus.setFocus(QtCore.Qt.MouseFocusReason)

    def mousePressEvent(self, event):
        # Remove the backed focus, if the widget is clicked, their is not
        # reason to restore the backed focus if the widget is left.
        self.backed_focus = None

        self.mode_manager.update(event, pressed=True)
        left = self.mode_manager.left_click_pressed
        if self.mode_manager.mode == ModeManager.SELECTION and left:
            self.selection_square.clicked(event.position())
        if self.mode_manager.mode == ModeManager.ZONE and left:
            self.zone_square.clicked(event.position())

    def mouseReleaseEvent(self, event):
        self.mode_manager.update(event, pressed=False)
        mode = self.mode_manager.mode
        if mode == ModeManager.SELECTION:
            clear_tree_selection(self.tree)
            if node := self.highlighter.current:
                node.selected = True
                self.nodeSelected.emit(node)
        elif mode == ModeManager.ZONE and (zone := self.zone_square.zone):
            self.zoneSelected.emit(zone)

        QtWidgets.QApplication.restoreOverrideCursor()
        self.selection_square.release()
        self.zone_square.release()
        self.repaint()

    def keyPressEvent(self, event):
        self.mode_manager.update(event, pressed=True)
        if event.key() == QtCore.Qt.Key_Up:
            self.highlighter.previous()
        elif event.key() == QtCore.Qt.Key_Down:
            self.highlighter.next()
        self.highlight()
        self.repaint()

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
        self.paintcontext.center = result
        self.repaint()

    def mouseMoveEvent(self, event):
        match self.mode_manager.mode:
            case ModeManager.SELECTION:
                nodes = hovered_nodes(
                    self.layers, event.position(), self.paintcontext)
                if self.selection_square.handeling:
                    self.selection_square.handle(event.position())
            case ModeManager.ZONE:
                nodes = []
                if self.zone_square.handeling:
                    self.zone_square.handle(event.position())
            case ModeManager.NAVIGATION:
                nodes = []
                offset = self.mode_manager.mouse_offset(event.position())
                if offset is not None:
                    x = self.paintcontext.center[0] + offset.x()
                    y = self.paintcontext.center[1] + offset.y()
                    self.paintcontext.center = [x, y]

        self.highlighter.set(nodes)
        self.highlight()

    def offset(self, point):
        return self.rect().center() + point.toPoint()

    def highlight(self):
        for node in self.layers:
            node.highlighted = node == self.highlighter.current
        self.repaint()

    def set_zone_mode(self, mode):
        self.mode_manager.zone_mode = mode

    def set_grid_visible(self, state):
        self.grid = state
        self.repaint()

    def set_boundaries_visible(self, state):
        self.boundaries = state
        self.repaint()

    @property
    def layers(self):
        return [
            n for l in list_layers(self.tree)
            for n in l.flat() if l.has_to_be_rendered]

    def paintEvent(self, _):
        if not self.tree:
            return

        painter = QtGui.QPainter()
        painter.begin(self)

        render_background(painter, self.data, self.paintcontext)

        higlighted, selected = None, None
        for node in self.layers:
            if not node.visible:
                continue

            if node.data.get("type") != NODE_TYPES.SET_STATIC:
                continue

            image = get_image(node.data)
            if not image:
                continue

            x, y = get_offset(node.data['position'], node.data['deph'], self.paintcontext)
            w, h = image.width(), image.height()
            rect = QtCore.QRect(x, y, w, h)
            rect = self.paintcontext.relatives_rect(rect)
            painter.drawImage(rect, image)
            if node.highlighted:
                higlighted = rect
            if node.selected:
                selected = rect

        sounds = self.tree.children[0].children[0].children
        for node in sounds:
            if not node.has_to_be_rendered:
                continue
            if rect := get_node_rect(node, self.paintcontext):
                image = get_image(node.data)
                render_sound(painter, node.data, rect, image, self.paintcontext)

        zones = self.tree.children[0].children[1].children
        for node in zones:
            if not node.has_to_be_rendered and not node.selected:
                continue
            image = get_image(node.data)
            render_zone(
                painter,
                node.data,
                node.selected,
                image,
                self.paintcontext)

        if self.grid:
            render_grid(
                painter,
                self.rect(),
                cctx.BLOCK_SIZE,
                self.paintcontext)

        if self.boundaries:
            render_boundaries(
                painter,
                self.data,
                self.paintcontext)

        if higlighted and self.mode_manager.mode != ModeManager.ZONE:
            painter.setBrush(QtCore.Qt.transparent)
            painter.setPen(QtCore.Qt.white)
            painter.drawRect(higlighted)

        if selected and self.mode_manager.mode != ModeManager.ZONE:
            painter.setBrush(QtCore.Qt.transparent)
            painter.setPen(QtCore.Qt.yellow)
            painter.drawRect(selected)

        if self.mode_manager.mode == ModeManager.SELECTION:
            square = self.selection_square
        else:
            square = self.zone_square

        render_selection_square(painter, square)
        rects = status_bar_rects(self.rect(), self.paintcontext)
        name = node.name if (node:=self.highlighter.current) else ''
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        render_scenewidget_status_bar(
            painter=painter,
            rects=rects,
            position=cursor,
            highlighted=name,
            paintcontext=self.paintcontext)

        if self.mode_manager.mode == ModeManager.ZONE:
            painter.end()
            return

        if (node:=self.highlighter.current) and (image:=get_image(node.data)):
            rect = status_thumbnail_rect(self.rect(), image, self.paintcontext)
            painter.drawImage(rect, image)

        painter.end()


def get_offset(pixel_position, deph, paintcontext):
    return pixel_position
    # hack to get deph (not working well but better than nothing)
    import math
    offset_x = math.ceil((pixel_position[0] - paintcontext.center[0]))
    offset_y = math.ceil((pixel_position[1] - paintcontext.center[1]))
    return [offset_x + (offset_x * deph), offset_y]


class ZoneSquare():
    def __init__(self, paintcontext):
        self.rect = None
        self.handeling = False
        self.paintcontext = paintcontext

    @property
    def zone(self):
        if not self.rect:
            return None
        point1 = self.paintcontext.absolute_point(self.rect.topLeft())
        point2 =  self.paintcontext.absolute_point(self.rect.bottomRight())
        l, t = to_block_position((point1.x(), point1.y()))
        r, b = to_block_position((point2.x(), point2.y()))
        return tuple(int(n) for n in (l, t, r, b))

    def clicked(self, cursor):
        self.handeling = True
        cursor = self.round_to_block(cursor)
        self.rect = QtCore.QRectF(cursor, cursor)

    def handle(self, cursor):
        cursor = self.round_to_block(cursor, rounded=True)
        self.rect.setBottomRight(cursor)

    def release(self):
        self.handeling = False
        self.rect = None

    def round_to_block(self, cursor, rounded=False):
        cursor = self.paintcontext.absolute_point(cursor)
        if rounded:
            x = int(round(cursor.x() / cctx.BLOCK_SIZE))
            y = int(round(cursor.y() / cctx.BLOCK_SIZE))
        else:
            x = int(cursor.x() / cctx.BLOCK_SIZE)
            y = int(cursor.y() / cctx.BLOCK_SIZE)
        point = QtCore.QPoint(x * cctx.BLOCK_SIZE, y * cctx.BLOCK_SIZE)
        return self.paintcontext.relative_point(point)


class SelectionSquare():
    def __init__(self, paintcontext):
        self.paintcontext = paintcontext
        self.tree = None
        self.rect = None
        self.handeling = False

    def clicked(self, cursor):
        self.handeling = True
        self.rect = QtCore.QRectF(cursor, cursor)

    def handle(self, cursor):
        self.rect.setBottomRight(cursor)
        nodes = [
            n for l in list_layers(self.tree)
            for n in l.flat() if n.has_to_be_rendered]
        rect = self.paintcontext.absolute_rect(self.rect)
        for node in nodes:
            nrect = get_node_rect(node, self.paintcontext)
            print(node, nrect)
            if not nrect:
                continue
            node.highlighted = rect.intersects(nrect)

    def release(self):
        self.handeling = False
        self.rect = None
        nodes = [
            n for l in list_layers(self.tree)
            for n in l.flat() if l.has_to_be_rendered]
        for node in nodes:
            node.highlighted = False


class NodeHighligther:
    def __init__(self):
        self.focus = -1
        self.nodes = []

    def set(self, nodes):
        self.nodes = list(reversed(nodes))
        if not (0 <= self.focus < len(self.nodes)):
            self.focus = 0 if nodes else -1

    def next(self):
        if self.focus < 0 or not self.nodes:
            return
        self.focus += 1
        if len(self.nodes) <= self.focus:
            self.focus = 0

    def previous(self):
        if self.focus < 0 or not self.nodes:
            return
        self.focus -= 1
        if self.focus < 0:
            self.focus = len(self.nodes) -1

    @property
    def current(self):
        if self.focus < 0:
            return None
        return self.nodes[self.focus]


class ModeManager:
    SELECTION = 'selection'
    NAVIGATION = 'navigation'
    ZONE = 'zone'

    def __init__(self):
        self.left_click_pressed = False
        self.mouse_ghost = None
        self.keys_pressed = set()
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
        self.zone_mode = False

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
        if self.zone_mode:
            return ModeManager.ZONE
        return ModeManager.SELECTION

    def mouse_offset(self, position):
        result = position - self.mouse_ghost if self.mouse_ghost else None
        self.mouse_ghost = position
        return result.toPoint() if result else None

