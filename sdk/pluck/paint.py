import os
from functools import partial

from PyQt5 import QtGui, QtCore
import corax.context as cctx

from pluck.qtutils import ICON_FOLDER, get_image
from pluck.geometry import grow_rect, get_position, pixel_position
from pluck.datas import GRAPHIC_TYPES, SOUND_TYPES, ZONE_TYPES


class PaintContext():
    def __init__(self, scene_datas):
        self.zoom = 1
        self._extra_zone = 200
        self.grid_color = "grey"
        self.grid_alpha = .2
        self.grid_border_color = "black"
        self.sound_zone_color = "blue"
        self.sound_fade_off = "red"
        self.background_color = "grey"
        self.zone_border_color = "white"
        self.zone_background_color = "white"
        self.cursor_background_color = "white"
        self.cursor_text_color = "white"
        self.cursor_background_alpha = 0.2
        self.zone_alpha = 0.2

    def relatives(self, value):
        return value * self.zoom

    def offset_rect(self, rect):
        rect.setLeft(rect.left() + self.extra_zone)
        rect.setTop(rect.top() + self.extra_zone)
        rect.setRight(rect.right() + self.extra_zone)
        rect.setBottom(rect.bottom() + self.extra_zone)

    def block_position(self, x, y):
        x -= self.extra_zone
        y -= self.extra_zone
        x //= (cctx.BLOCK_SIZE * self.zoom)
        y //= (cctx.BLOCK_SIZE * self.zoom)
        return x, y

    def zone_contains_block_position(self, zone, x, y):
        l, t, r, b = [n // cctx.BLOCK_SIZE for n in zone]
        return l <= x <= r and t <= y <= b

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


def render_handler(painter, block_in, block_out, paintcontext):
    x = min([block_in[0], block_out[0]])
    y = min([block_in[1], block_out[1]])
    x2 = max([block_in[0], block_out[0]])
    y2 = max([block_in[1], block_out[1]])
    size = cctx.BLOCK_SIZE * paintcontext.zoom
    l, t, r, b = x * size, y * size, x2 * size, y2 * size
    w, h = r - l + size, b - t + size
    rect = QtCore.QRect(l, t, w, h)
    paintcontext.offset_rect(rect)
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
    color = QtGui.QColor(paintcontext.cursor_background_color)
    color.setAlphaF(paintcontext.cursor_background_alpha)
    painter.setBrush(QtGui.QBrush(color))
    painter.drawRect(rect)


def render_zone(painter, zone_datas, image, paintcontext):
    x, y = pixel_position(zone_datas["zone"][:2])
    z, a = pixel_position(zone_datas["zone"][2:])
    l = paintcontext.relatives(x)
    t = paintcontext.relatives(y)
    r = paintcontext.relatives(z)
    b = paintcontext.relatives(a)
    rect = QtCore.QRectF(l, t, r-l, b-t)
    paintcontext.offset_rect(rect)

    pen = QtGui.QPen(QtGui.QColor(paintcontext.zone_border_color))
    pen.setWidth(3)
    color = QtGui.QColor(paintcontext.zone_background_color)
    color.setAlphaF(paintcontext.zone_alpha)
    brush = QtGui.QBrush(color)
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)

    l = rect.center().x() - (image.size().width() / 2)
    t = rect.center().y() - (image.size().height() / 2)
    point = QtCore.QPointF(l, t)
    painter.drawImage(point, image)


def render_cursor(painter, block_position, paintcontext):
    x, y = block_position
    size = cctx.BLOCK_SIZE * paintcontext.zoom
    rect = QtCore.QRect(x * size, y * size, size, size)
    paintcontext.offset_rect(rect)
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
    color = QtGui.QColor(paintcontext.cursor_background_color)
    color.setAlphaF(paintcontext.cursor_background_alpha)
    painter.setBrush(QtGui.QBrush(color))
    painter.drawRect(rect)

    color = QtGui.QColor(paintcontext.cursor_text_color)
    painter.setPen(QtGui.QPen(color))
    painter.setBrush(QtGui.QBrush(color))
    option = QtGui.QTextOption()
    flags = QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft
    option.setAlignment(flags)
    font = QtGui.QFont()
    font.setBold(True)
    font.setPixelSize(15)
    painter.setFont(font)
    text = f"({int(x)}, {int(y)})"
    x, y = rect.right(), rect.bottom()
    painter.drawText(QtCore.QRectF(x + 10, y + 10, 200, 200), flags, text)


def get_renderer(element):
    if element is None:
        return
    elif element["type"] == "scene":
        return partial(render_background, scene_datas=element)
    elif element["type"] in SOUND_TYPES:
        image = get_image(element)
        return partial(render_sound, sound_datas=element, image=image)
    elif element["type"] in ZONE_TYPES:
        image = get_image(element)
        return partial(render_zone, zone_datas=element, image=image)
    elif element["type"] in GRAPHIC_TYPES:
        image = get_image(element)
        x, y = get_position(element)
        return partial(render_image, image=image, x=x, y=y)


def render_background(painter, scene_datas, paintcontext):

    boundary = scene_datas["boundary"]
    x = paintcontext.relatives(boundary[0])
    y = paintcontext.relatives(boundary[1])
    w = paintcontext.relatives(boundary[0] + boundary[2])
    h = paintcontext.relatives(boundary[1] + boundary[3])
    rect = QtCore.QRectF(x, y, w, h)
    paintcontext.offset_rect(rect)

    pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
    brush = QtGui.QBrush(QtGui.QColor(paintcontext.background_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(grow_rect(rect, paintcontext.extra_zone))
    brush = QtGui.QBrush(QtGui.QColor(*scene_datas["background_color"]))
    painter.setBrush(brush)
    painter.drawRect(rect)

    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    painter.setBrush(brush)


def render_image(painter, image, x, y, paintcontext):
    x = paintcontext.relatives(x)
    y = paintcontext.relatives(y)
    w = paintcontext.relatives(image.size().width())
    h = paintcontext.relatives(image.size().height())
    rect = QtCore.QRectF(x, y, w, h)
    paintcontext.offset_rect(rect)
    painter.drawImage(rect, image)


def render_sound(painter, sound_datas, image, paintcontext):
    if sound_datas["zone"] is None:
        return
    rect = QtCore.QRectF()
    rect.setLeft(paintcontext.relatives(sound_datas["zone"][0]))
    rect.setTop(paintcontext.relatives(sound_datas["zone"][1]))
    rect.setRight(paintcontext.relatives(sound_datas["zone"][2]))
    rect.setBottom(paintcontext.relatives(sound_datas["zone"][3]))
    paintcontext.offset_rect(rect)

    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    pen = QtGui.QPen(QtGui.QColor(paintcontext.sound_zone_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)

    falloff = paintcontext.relatives(sound_datas["falloff"])
    rect = grow_rect(rect, -falloff)

    pen = QtGui.QPen(QtGui.QColor(paintcontext.sound_fade_off))
    pen.setStyle(QtCore.Qt.DashLine)
    painter.setPen(pen)
    painter.setBrush(brush)

    painter.drawRect(rect)

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