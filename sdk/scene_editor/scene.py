from PyQt5 import QtWidgets, QtGui
from scene_editor.tree import list_sounds, list_layers
from scene_editor.paint import PaintContext, render_grid


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
        nodes = [n for l in list_layers(self.tree) for n in l.flat()]
        for node in nodes:
            node.render(painter, self.paintcontext)
        render_grid(
            painter,
            self.rect(),
            self.coraxcontext.BLOCK_SIZE,
            scene_datas["grid_pixel_offset"],
            self.paintcontext)
        for sound in list_sounds(self.tree):
            sound.render(painter, self.paintcontext)
