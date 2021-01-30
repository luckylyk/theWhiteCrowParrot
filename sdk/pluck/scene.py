from PyQt5 import QtWidgets, QtGui
from pluck.tree import list_sounds, list_layers, list_zones
from pluck.paint import PaintContext, render_grid


class SceneWidget(QtWidgets.QWidget):
    def __init__(self, tree, coraxcontext, paintcontext, parent=None):
        super().__init__(parent=parent)
        self.paintcontext = paintcontext
        self.tree = tree
        self.coraxcontext = coraxcontext
        self.recompute_size()

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
