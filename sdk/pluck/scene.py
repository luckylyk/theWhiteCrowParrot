from PyQt5 import QtWidgets, QtGui, QtCore
from pluck.tree import list_sounds, list_layers, list_zones, get_scene
from pluck.paint import PaintContext, render_grid, render_cursor, render_handler
import corax.context as cctx


ZONE_TEMPLATE = """
zone selected: {0}

template for zone node:
        {{
            "name": "unnamed",
            "type": "no_go",
            "affected": null,
            "zone": {0}
        }}
"""


class SceneWidget(QtWidgets.QWidget):
    def __init__(self, tree, coraxcontext, paintcontext, parent=None):
        super().__init__(parent=parent)
        self.paintcontext = paintcontext
        self.tree = tree
        self.coraxcontext = coraxcontext
        self.recompute_size()
        self.setMouseTracking(True)
        self.block_position = None
        self.block_position_backed_up = None
        self.is_handeling = False

    def mousePressEvent(self, event):
        if not self.block_position:
            return
        x, y = self.block_position
        zone = get_scene(self.tree).data["boundary"]
        if self.paintcontext.zone_contains_block_position(zone, x, y):
            self.block_position_backed_up = self.block_position
        self.is_handeling = True

    def mouseReleaseEvent(self, event):
        if not self.block_position_backed_up or not self.is_handeling:
            self.is_handeling = False
            self.block_position_backed_up = None
            self.repaint()
            return

        self.is_handeling = False
        x = min([self.block_position[0], self.block_position_backed_up[0]])
        y = min([self.block_position[1], self.block_position_backed_up[1]])
        x2 = max([self.block_position[0], self.block_position_backed_up[0]])
        y2 = max([self.block_position[1], self.block_position_backed_up[1]])
        mesagebox = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.NoIcon,
            "Zone selected:",
            ZONE_TEMPLATE.format(list(map(int, [x, y, x2 + 1, y2 + 1]))),
            QtWidgets.QMessageBox.Ok)
        mesagebox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        mesagebox.exec_()
        self.repaint()

    def mouseMoveEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.block_position = self.paintcontext.block_position(x, y)
        self.repaint()

    def recompute_size(self):
        scene_datas = self.tree.children[0].data
        w, h = scene_datas["boundary"][2], scene_datas["boundary"][3]
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
        scene_datas = self.tree.children[0].data
        self.tree.children[0].render(painter, self.paintcontext)
        nodes = [
            n for l in list_layers(self.tree)
            for n in l.flat() if l.has_to_be_rendered]

        for node in nodes:
            if node.visible:
                node.render(painter, self.paintcontext)
        render_grid(
            painter,
            self.rect(),
            self.coraxcontext.BLOCK_SIZE,
            scene_datas["grid_pixel_offset"],
            self.paintcontext)
        for sound in list_sounds(self.tree):
            if sound.has_to_be_rendered:
                sound.render(painter, self.paintcontext)
        for zone in list_zones(self.tree):
            if zone.has_to_be_rendered:
                zone.render(painter, self.paintcontext)

        if self.is_handeling is True and self.block_position_backed_up:
            bi, bo = self.block_position, self.block_position_backed_up
            render_handler(painter, bi, bo, self.paintcontext)
        elif self.block_position is not None:
            zone = get_scene(self.tree).data["boundary"]
            x, y = self.block_position
            if self.paintcontext.zone_contains_block_position(zone, x, y):
                render_cursor(painter, self.block_position, self.paintcontext)