import os
from PyQt5 import QtGui, QtCore
from scene_editor.qtutils import ICON_FOLDER
from scene_editor.geometry import grow_rect


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