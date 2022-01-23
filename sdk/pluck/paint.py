

from PySide6 import QtGui, QtCore

import corax.context as cctx
from corax.coordinate import to_pixel_position, to_block_position
from pluck.geometry import grow_rect, pixel_position


class PaintContext():
    background_color = "grey"
    cursor_background_alpha = 0.2
    cursor_background_color = "white"
    cursor_text_color = "white"
    frame_number_color = "red"
    grid_color = "grey"
    grid_alpha = .2
    grid_border_color = "black"
    hard_boundary_color = "black"
    hard_boundary_width = 2
    selection_color = "blue"
    sound_fade_off = "red"
    sound_zone_color = "blue"
    status_bar_height = 30
    status_bar_pos_width = 200
    status_bar_text_color = "black"
    status_bar_text_padding = 5
    status_bar_text_size = 15
    status_bar_color = "grey"
    soft_boundary_color = "grey"
    soft_boundary_width = 1
    thumbnail_max_size = 200
    zone_border_width = 2
    zone_alpha = 0.2
    zone_border_color = "white"
    zone_background_color = "white"

    def __init__(self):
        self._extra_zone = 200
        self.zoom = 1
        self.center = [0, 0]

    def relatives(self, value):
        return value * self.zoom

    def absolute(self, value):
        return value / self.zoom

    def absolute_rect(self, rect):
        top_left = self.absolute_point(rect.topLeft())
        width = self.absolute(rect.width())
        height = self.absolute(rect.height())
        return QtCore.QRectF(top_left.x(), top_left.y(), width, height)

    def block_position(self, x, y):
        x = self.absolute(x)
        y = self.absolute(y)
        return to_block_position((x, y))

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


def render_background(painter, data, paintcontext):
    painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
    color = QtGui.QColor(*data['background_color'])
    painter.setBrush(QtGui.QBrush(color))
    rect = QtCore.QRect()
    rect.setLeft(data['boundary'][0])
    rect.setTop(data['boundary'][1])
    rect.setRight(data['boundary'][2])
    rect.setBottom(data['boundary'][3])
    rect = paintcontext.relatives_rect(rect)
    painter.drawRect(rect)


def render_boundaries(painter, data, paintcontext):
    rect = QtCore.QRect()
    rect.setLeft(data['boundary'][0])
    rect.setTop(data['boundary'][1])
    rect.setRight(data['boundary'][2])
    rect.setBottom(data['boundary'][3])
    rect = paintcontext.relatives_rect(rect)
    rect = grow_rect(rect, paintcontext.hard_boundary_width / 2)
    pen = QtGui.QPen(QtGui.QColor(paintcontext.hard_boundary_color))
    pen.setWidth(paintcontext.hard_boundary_width)
    painter.setPen(pen)
    painter.setBrush(QtCore.Qt.transparent)
    painter.drawRect(rect)

    pen = QtGui.QPen(QtGui.QColor(paintcontext.soft_boundary_color))
    pen.setWidth(paintcontext.soft_boundary_width)
    pen.setStyle(QtCore.Qt.DashLine)
    painter.setPen(pen)
    for boundary in data['soft_boundaries']:
        rect = QtCore.QRect()
        rect.setLeft(boundary[0])
        rect.setTop(boundary[1])
        rect.setRight(boundary[2])
        rect.setBottom(boundary[3])
        rect = paintcontext.relatives_rect(rect)
        painter.drawRect(rect)


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
    l, t = pixel_position(zone_data["zone"][:2])
    r, b = pixel_position(zone_data["zone"][2:])
    rect = paintcontext.relatives_rect(QtCore.QRectF(l, t, r-l, b-t))
    rect = grow_rect(rect, paintcontext.zone_border_width / 2)

    pen = QtGui.QPen(QtGui.QColor(paintcontext.zone_border_color))
    pen.setWidth(paintcontext.zone_border_width)
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
    flags = QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft
    font = QtGui.QFont()
    font.setBold(True)
    font.setPixelSize(15)
    painter.setFont(font)
    text = f"({int(x)}, {int(y)})"
    x, y = rect.right(), rect.bottom()
    painter.drawText(QtCore.QRectF(x + 10, y + 10, 200, 200), flags, text)


def render_image(painter, image, x, y, paintcontext):
    x = paintcontext.relatives(x)
    y = paintcontext.relatives(y)
    w = paintcontext.relatives(image.size().width())
    h = paintcontext.relatives(image.size().height())
    rect = QtCore.QRectF(x, y, w, h)
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


def render_hitmap(painter, hitmap, color, paintcontext):
    color = QtGui.QColor(*color)
    color.setAlphaF(0.25)
    painter.setBrush(QtGui.QBrush(color))
    painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
    for block in hitmap:
        x, y = paintcontext.offset(*to_pixel_position(block))
        x = paintcontext.relatives(x)
        y = paintcontext.relatives(y)
        size = paintcontext.relatives(cctx.BLOCK_SIZE)
        rect = QtCore.QRectF(x, y, size, size)
        painter.drawRect(rect)


def render_selection_square(painter, selection_square, paintcontext=None):
    rect = selection_square.rect
    if not rect:
        return
    paintcontext = paintcontext or PaintContext()
    rect = paintcontext.relatives_rect(rect)
    bordercolor = QtGui.QColor(paintcontext.selection_color)
    backgroundcolor = QtGui.QColor(paintcontext.selection_color)
    backgroundcolor.setAlpha(85)
    painter.setPen(QtGui.QPen(bordercolor))
    painter.setBrush(QtGui.QBrush(backgroundcolor))
    painter.drawRect(rect)


def render_node_border(painter, data, selected, highlighted, paintcontext):
    paintcontext = paintcontext or PaintContext()
    l, t, r, b = data['zone']
    rect = QtCore.QRectF(l, t, r-l, b-t)
    rect = paintcontext.relatives_rect(rect)
    if selected:
        color = QtGui.QColor("white")
    elif highlighted:
        color = QtGui.QColor("yellow")
    else:
        color = QtCore.Qt.transparent
    pen = QtGui.QPen(color)
    brush = QtGui.QBrush(QtCore.Qt.transparent)
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(rect)


def render_scenewidget_status_bar(
        painter, rects, position, highlighted, paintcontext):
    painter.setPen(QtGui.QPen(QtCore.Qt.transparent))
    painter.setBrush(QtGui.QBrush(QtGui.QColor(paintcontext.status_bar_color)))
    painter.drawRect(rects['bar'])

    painter.setPen(QtGui.QPen(paintcontext.status_bar_text_color))
    font = QtGui.QFont()
    font.setPixelSize(paintcontext.status_bar_text_size)
    painter.setFont(font)
    flags =  QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

    pos = paintcontext.absolute_point(position)
    text = f'pixel position: ({int(pos.x()):05d} - {int(pos.y()):05d})'
    painter.drawText(rects['pixel_coord'], flags, text)

    x, y = to_block_position((pos.x(), pos.y()))
    text = f'block position: ({int(x):04d} - {int(y):04d})'
    painter.drawText(rects['block_coord'], flags, text)

    painter.drawText(rects['highlighted'], flags, highlighted)