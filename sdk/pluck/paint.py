
from functools import partial

from PySide6 import QtGui, QtCore
import corax.context as cctx
from corax.coordinate import to_pixel_position

from pluck.qtutils import get_image
from pluck.geometry import grow_rect, get_position, pixel_position
from pluck.data import GRAPHIC_TYPES, SOUND_TYPES, ZONE_TYPES



class PaintContext():
    def __init__(self):
        self.zoom = 1
        self.center = [0, 0]
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
        self.frame_number_color = "red"
        self.cursor_text_color = "white"
        self.cursor_background_alpha = 0.2
        self.zone_alpha = 0.2

    def relatives(self, value):
        return value * self.zoom

    def absolute(self, value):
        return value / self.zoom

    def absolute_point(self, point):
        return QtCore.QPointF(
            self.absolute(point.x() - self.center[0]),
            self.absolute(point.y() - self.center[1]))

    def relative_point(self, point):
        return QtCore.QPointF(
            self.relatives(point.x()) + self.center[0],
            self.relatives(point.y()) + self.center[1])

    def relatives_rect(self, rect):
        return QtCore.QRectF(
            (rect.left() * self.zoom) + self.center[0],
            (rect.top() * self.zoom) + self.center[1],
            rect.width() * self.zoom,
            rect.height() * self.zoom)

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

    def zoomin(self, vector=None):
        self.zoom += self.zoom / 10
        self.zoom = min(self.zoom, 5)

    def zoomout(self):
        self.zoom -= self.zoom / 10
        self.zoom = max(self.zoom, .1)

    def reset(self):
        self.center = [0, 0]
        self.zoom = 1


def render_center(painter, center, offset, paintcontext):
    pen_width = paintcontext.relatives(1)
    painter.setBrush(QtGui.QBrush(QtCore.Qt.transparent))
    pen = QtGui.QPen(QtCore.Qt.blue)
    pen.setWidthF(pen_width)
    painter.setPen(pen)
    center_x = paintcontext.relatives(center[0])
    center_y = paintcontext.relatives(center[1])
    point = QtCore.QPointF(center_x, center_y)
    width = paintcontext.relatives(2)
    painter.drawEllipse(point, width, width)

    if not offset:
        return

    pen = QtGui.QPen(QtCore.Qt.yellow)
    pen.setWidthF(pen_width)
    painter.setPen(pen)
    offset_x = paintcontext.relatives(offset[0]) + center_x
    offset_y = paintcontext.relatives(offset[1]) + center_y
    point = QtCore.QPointF(offset_x, offset_y)
    width = paintcontext.relatives(3)
    painter.drawEllipse(point, width, width)

    pen = QtGui.QPen(QtCore.Qt.red)
    pen.setWidthF(pen_width)
    pen.setStyle(QtCore.Qt.DashLine)
    painter.setPen(pen)
    painter.drawLine(center_x, center_y, offset_x, offset_y)


def render_trigger(painter, name, rect, paintcontext):
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
    painter.drawText(rect, flags, name)


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


def render_zone(painter, zone_data, image, paintcontext):
    x, y = pixel_position(zone_data["zone"][:2])
    z, a = pixel_position(zone_data["zone"][2:])
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
        return partial(
            render_background,
            rect=element["boundary"],
            color=element["background_color"])
    elif element["type"] in SOUND_TYPES:
        image = get_image(element)
        return partial(render_sound, sound_data=element, image=image)
    elif element["type"] in ZONE_TYPES:
        image = get_image(element)
        return partial(render_zone, zone_data=element, image=image)
    elif element["type"] in GRAPHIC_TYPES:
        image = get_image(element)
        x, y = get_position(element)
        return partial(render_image, image=image, x=x, y=y)


def render_background(painter, rect, color, paintcontext):
    x = paintcontext.relatives(rect[0])
    y = paintcontext.relatives(rect[1])
    w = paintcontext.relatives(rect[0] + rect[2])
    h = paintcontext.relatives(rect[1] + rect[3])
    rect = QtCore.QRectF(x, y, w, h)
    paintcontext.offset_rect(rect)

    pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 0))
    brush = QtGui.QBrush(QtGui.QColor(paintcontext.background_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(grow_rect(rect, paintcontext.extra_zone))
    brush = QtGui.QBrush(QtGui.QColor(*color))
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
    rect = paintcontext.relatives_rect(rect)
    painter.drawImage(rect, image)


def render_sound(painter, sound_data, rect, image, paintcontext):
    if sound_data["zone"] is None:
        return

    brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
    pen = QtGui.QPen(QtGui.QColor(paintcontext.sound_zone_color))
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)

    falloff = paintcontext.relatives(sound_data["falloff"])
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


def render_grid(painter, rect, block_size, paintcontext=None):
    rect = grow_rect(rect, -paintcontext.extra_zone)
    block_size = paintcontext.relatives(block_size)
    l = rect.left()
    t = rect.top()
    r = rect.right()
    b = rect.bottom()
    grid_color = QtGui.QColor(paintcontext.grid_color)
    grid_color.setAlphaF(paintcontext.grid_alpha)
    pen = QtGui.QPen(grid_color)
    painter.setPen(pen)
    x = block_size + (paintcontext.center[0] % block_size)
    y = block_size + (paintcontext.center[1] % block_size)
    while x < r:
        painter.drawLine(x, t, x, b)
        x += block_size
    while y < b:
        painter.drawLine(l, y, r, y)
        y += block_size
    painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
    pen = QtGui.QPen(QtGui.QColor(paintcontext.grid_border_color))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.drawRect(rect)


def render_hitbox(painter, hitbox, color, paintcontext):
    color = QtGui.QColor(*color)
    color.setAlphaF(0.25)
    painter.setBrush(QtGui.QBrush(color))
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
    for block in hitbox:
        x, y = paintcontext.offset(*to_pixel_position(block))
        x = paintcontext.relatives(x)
        y = paintcontext.relatives(y)
        size = paintcontext.relatives(cctx.BLOCK_SIZE)
        rect = QtCore.QRectF(x, y, size, size)
        painter.drawRect(rect)