

from math import atan2, sin, cos, radians, pi
import colorsys
import sys


class ColorBalance(QtWidgets.QWidget):
    currentColorChanged = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('ColorBalance')
        self.resize(150, 150)
        self.hue = 1.0
        self.saturation = 0.0
        self.value = 1.0
        self.huesat_wheel = HueSatWheel()
        self.huesat_wheel.currentColorChanged.connect(self.on_hue_sat_changed)
        self.value_slider = ValueSlider()
        self.value_slider.sliderMoved.connect(self.on_value_changed)
        self.rgb_label = {}
        self.rgb_label = {
            'r': QtWidgets.QLabel(),
            'g': QtWidgets.QLabel(),
            'b': QtWidgets.QLabel()}
        for color, widget in self.rgb_label.items():
            widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
            widget.setFrameShadow(QtWidgets.QFrame.Plain)
            widget.setLineWidth(1)
        self.update_rgb()
        self.set_layout()

    def set_layout(self):
        colorwheel_layout = QtWidgets.QHBoxLayout()
        colorwheel_layout.addWidget(self.huesat_wheel)
        colorwheel_layout.addWidget(self.value_slider)
        rgb_layout = QtWidgets.QHBoxLayout()
        rgb_layout.addWidget(self.rgb_label['r'])
        rgb_layout.addWidget(self.rgb_label['g'])
        rgb_layout.addWidget(self.rgb_label['b'])
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(colorwheel_layout)
        vbox.addLayout(rgb_layout)
        self.setLayout(vbox)

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

    def set_rgb(self, r, g, b):
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self.hue = h
        self.saturation = s
        self.value = v
        self.huesat_wheel.hue = h
        self.huesat_wheel.saturation = s
        self.huesat_wheel.update_color_point()
        self.value_slider.value = v
        self.update_rgb()

    def update_rgb(self):
        self.currentColorChanged.emit(self.rgb())
        r, g, b = self.rgb()
        self.rgb_label['r'].setText(f'{r:.2f}')
        self.rgb_label['g'].setText(f'{g:.2f}')
        self.rgb_label['b'].setText(f'{b:.2f}')


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
        painter = QtGui.QPainter(self)
        # Gradient
        gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, self.height())
        white_color = QtGui.QColor()
        color = 1.0 * self.value if self.value <= 1.0 else 1.0
        white_color.setRgbF(color, color, color)
        black_color = QtGui.QColor()
        if self.value >= 1.0:
            color = min((1.0 * self.value) - 1.0, 1.0)
        else:
            color = 0.0
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
        self._drag_origin = QtGui.QCursor().pos()
        self._start_origin = self.value
        self.grabMouse()

    def mouseMoveEvent(self, event):
        current_position = QtGui.QCursor().pos()
        offset_pixel = self._drag_origin.y() - current_position.y()
        offset = offset_pixel / self.DIVIDED_INCREMENT
        self.value = self._start_origin + offset
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

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # ColorWheel image
        # self._paint_colorwheel(painter)  # too slow
        # texture brush is more efficient
        brush = QtGui.QBrush()
        brush.setTextureImage(self._colorwheel_image)
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.transparent)
        # drawRect needed to draw texture brush?
        painter.drawRect(0, 0, self.width(), self.height())

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
        self.mouse_update(event)

    def mouseMoveEvent(self, event):
        self.mouse_update(event)

    def mouse_update(self, event):
        self._color_point.setX(event.pos().x())
        self._color_point.setY(event.pos().y())
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
        for x in range(self.width()):
            for y in range(self.height()):
                color = QtGui.QColor(0.0)
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
