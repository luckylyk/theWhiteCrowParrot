"""
Forked module from
https://github.com/vincentgires/qtutils/blob/master/qtutils/widgets/color.py
Author: Vincent Gires
"""

from PySide6 import QtWidgets, QtCore, QtGui
from math import atan2, sin, cos, radians, pi, sqrt
import colorsys


def distance2d(point1, point2):
    return sqrt(
        ((point2[0] - point1[0]) ** 2) +
        ((point2[1] - point1[1]) ** 2))


class ColorWheel(QtWidgets.QWidget):
    currentColorChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedSize(196, 232)
        self.hue = 1.0
        self.saturation = 0.0
        self.value = 1.0
        self.huesat_wheel = HueSatWheel()
        self.huesat_wheel.currentColorChanged.connect(self.on_hue_sat_changed)
        self.value_slider = ValueSlider()
        self.value_slider.sliderMoved.connect(self.on_value_changed)
        self.color_square = ColorSquare(self.rgb())
        self.color_square.setFixedSize(173, 20)
        self.rgb_edits = [QtWidgets.QLineEdit() for _ in range(3)]
        validator = QtGui.QIntValidator()
        validator.setRange(0, 255)
        for edit in self.rgb_edits:
            edit.textEdited.connect(self.set_rgb_from_edit)
            edit.setValidator(validator)
        self.update_rgb()

        colorwheel_layout = QtWidgets.QHBoxLayout()
        colorwheel_layout.addWidget(self.huesat_wheel)
        colorwheel_layout.addWidget(self.value_slider)
        rgb_layout = QtWidgets.QHBoxLayout()
        for widget in self.rgb_edits:
            rgb_layout.addWidget(widget)

        vbox = QtWidgets.QVBoxLayout(self.widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(colorwheel_layout)
        vbox.addWidget(self.color_square)
        vbox.addLayout(rgb_layout)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSizeConstraint(QtWidgets.QBoxLayout.SetMaximumSize)
        hbox.addStretch(1)
        hbox.addWidget(self.widget)
        hbox.addStretch(1)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(hbox)
        self.layout.addStretch(1)

    def on_hue_sat_changed(self, hue_sat_value):
        if not hue_sat_value:
            return
        h, s, _ = hue_sat_value
        self.hue = h
        self.saturation = s
        self.update_rgb()

    def on_value_changed(self, value):
        if not value:
            return
        self.value = value
        self.update_rgb()

    def rgb(self):
        return colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)

    def rgb255(self):
        return [round(c * 255) for c in self.rgb()]

    def set_rgb255(self, r, g, b):
        self.blockSignals(True)
        self.set_rgb(r / 255, g / 255, b / 255)
        self.blockSignals(False)

    def set_rgb(self, r, g, b, update_rgb_edits=True):
        # Need to clamp the value because unfortunately QDoubleValidator.setTop
        # is not working properly.
        h, s, v = colorsys.rgb_to_hsv(min(r, 1.0), min(g, 1.0), min(b, 1.0))
        self.hue = h
        self.saturation = s
        self.value = v
        self.huesat_wheel.hue = h
        self.huesat_wheel.saturation = s
        self.huesat_wheel.update_color_point()
        self.value_slider.value = v
        if update_rgb_edits:
            self.update_rgb()

    def update_rgb(self):
        self.color_square.set_rgb(*self.rgb255())
        self.currentColorChanged.emit(self.rgb())
        for widget, color in zip(self.rgb_edits, self.rgb()):
            widget.setText(f'{round(color * 255)}')

    def set_rgb_from_edit(self):
        r, g, b = [float(edit.text() or "0.0") / 255 for edit in self.rgb_edits]
        self.set_rgb(r, g, b, update_rgb_edits=False)


class ColorSquare(QtWidgets.QWidget):

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QtGui.QColor(*color)

    def set_rgb(self, r, g, b):
        self.color = QtGui.QColor(r, g, b)
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
        painter.setBrush(self.color)
        painter.drawRect(self.rect())
        painter.end()


class ValueSlider(QtWidgets.QWidget):
    FIXED_WIDTH = 10
    DIVIDED_INCREMENT = 100
    SELECT_SIZE = 4
    GRID_NUMBER = 15
    sliderMoved = QtCore.Signal(float)

    def __init__(self, value=1.0, parent=None):
        super().__init__(parent)
        self.value = value
        self._drag_origin = None
        self._start_origin = None
        self.setFixedWidth(self.FIXED_WIDTH)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Gradient
        gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, self.height())
        white_color = QtGui.QColor()
        color = 1.0 * self.value if self.value <= 1.0 else 1.0
        white_color.setRgbF(color, color, color)
        black_color = QtGui.QColor()
        color = min((1.0 * self.value) - 1.0, 1.0) if self.value >= 1.0 else 0.0
        black_color.setRgbF(color, color, color)
        gradient.setColorAt(0, white_color)
        gradient.setColorAt(1, black_color)
        painter.fillRect(0, 0, self.width(), self.height(), gradient)

        # Selected color point
        painter.setPen(QtCore.Qt.darkGray)
        for i in range(self.GRID_NUMBER):
            d = (self.height() / self.GRID_NUMBER)
            step_y = (i * d) + (d / 2)
            size = self.SELECT_SIZE / 2
            pos_x = QtCore.QPoint((self.width() / 2) - size - 1, step_y)
            pos_y = QtCore.QPoint((self.width() / 2) + size, step_y)
            line = QtCore.QLine(pos_x, pos_y)
            painter.drawLine(line)

        painter.end()

    def mousePressEvent(self, event):
        self._drag_origin = QtGui.QCursor.pos()
        self._start_origin = self.value
        self.grabMouse()

    def mouseMoveEvent(self, event):
        if not self._drag_origin:
            return
        current_position = QtGui.QCursor.pos()
        offset_pixel = self._drag_origin.y() - current_position.y()
        offset = offset_pixel / self.DIVIDED_INCREMENT
        self.value = self._start_origin + offset
        if self.value < 0.0:
            self.value = 0
        elif self.value > 1.0:
            self.value = 1.0
        self.sliderMoved.emit(self.value)
        self.repaint()

    def mouseReleaseEvent(self, event):
        self.releaseMouse()
        self._drag_origin = None
        self._start_origin = None

    def enterEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.SplitVCursor))

    def leaveEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))


class HueSatWheel(QtWidgets.QWidget):
    SELECT_RADIUS = 3
    MININUM_SIZE = 100
    currentColorChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(100, 100)
        self.setMinimumSize(self.MININUM_SIZE, self.MININUM_SIZE)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.hue = 1.0
        self.saturation = 0.0
        self.value = 1.0
        self._color_point = QtCore.QPoint()
        self._colorwheel_image = None
        self._mouse_clicked = False

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        # ColorWheel image
        # self._paint_colorwheel(painter)  # too slow
        # texture brush is more efficient
        brush = QtGui.QBrush()
        # brush.setTextureImage(self._colorwheel_image)
        painter.setBrush(QtCore.Qt.transparent)
        painter.setPen(QtCore.Qt.transparent)
        # drawRect needed to draw texture brush?
        if self._colorwheel_image:
            painter.drawImage(self.rect(), self._colorwheel_image)

        # Selected color point
        painter.setPen(QtCore.Qt.darkGray)
        painter.setBrush(QtCore.Qt.white)
        painter.drawEllipse(
            self._color_point, self.SELECT_RADIUS, self.SELECT_RADIUS)
        painter.end()

    def resizeEvent(self, event):
        # TODO: scale image for better performance
        # Regenerate image
        self._colorwheel_image = self._create_colorwheel_image()
        self.update_color_point()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_clicked = True
            self.mouse_update(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_clicked = False

    def mouseMoveEvent(self, event):
        if not self._mouse_clicked:
            return
        self.mouse_update(event)

    def mouse_update(self, event):
        center = self.rect().center()
        pos = event.position()
        radius = ((self.width() + self.height()) / 4) + 3
        if distance2d((pos.x(), pos.y()), (center.x(), center.y())) > radius:
            return
        self._color_point.setX(event.position().x())
        self._color_point.setY(event.position().y())
        self.set_hue_sat_from_pos()
        self.currentColorChanged.emit(self.hsv())
        self.repaint()

    def _get_hue_sat_from_coords(self, x, y):
        radius = min(self.width(), self.height()) / 2
        center_x, center_y = self.width() / 2, self.height() / 2
        rx, ry = x - center_x, y - center_y
        sat = ((rx ** 2 + ry ** 2) ** 0.5) / radius
        if sat <= 1.0:
            hue = ((atan2(ry, rx) / pi) + 1) / 2
            return hue, sat

    def _get_coords_from_hue_sat(self, hue, sat):
        radius = min(self.width(), self.height()) / 2
        center_x, center_y = self.width() / 2, self.height() / 2
        angle = radians(hue * 360)
        angle = angle + radians(180)  # rotate to match colorwheel image
        x = (sat * radius) * cos(angle) + center_x
        y = (sat * radius) * sin(angle) + center_y
        return x, y

    def _paint_colorwheel(self, painter):
        center = self.rect().center()
        radius = ((self.width() + self.height()) / 4) - 1.5
        for x in range(self.width()):
            for y in range(self.height()):
                if distance2d((x, y), (center.x(), center.y())) > radius:
                    continue
                color = QtGui.QColor()
                color.setAlphaF(0.0)
                hue_sat = self._get_hue_sat_from_coords(x, y)
                if hue_sat:
                    hue, sat = hue_sat
                    value = 1.0 * self.value if self.value <= 1.0 else 1.0
                    color.setHsvF(hue, sat, value, 1.0)
                painter.setPen(color)
                painter.drawPoint(x, y)

    def _create_colorwheel_image(self):
        """QImage is created once to speed up repaint
        Image is regenerate when window is resized"""
        image = QtGui.QImage(
            self.width(), self.height(), QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)
        brush = QtGui.QBrush()
        brush.setColor(QtCore.Qt.red)
        painter = QtGui.QPainter(image)
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self._paint_colorwheel(painter)
        painter.end()
        return image

    def set_hue_sat_from_pos(self):
        x, y = self._color_point.x(), self._color_point.y()
        hue_sat = self._get_hue_sat_from_coords(x, y)
        if hue_sat:
            self.hue, self.saturation = hue_sat

    def update_color_point(self):
        h, s, _ = self.hsv()
        x, y = self._get_coords_from_hue_sat(h, s)
        self._color_point.setX(x)
        self._color_point.setY(y)
        self.repaint()

    def hsv(self):
        return self.hue, self.saturation, self.value
