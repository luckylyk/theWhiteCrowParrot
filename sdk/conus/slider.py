import math
from PySide6 import QtGui, QtCore, QtWidgets


SLIDER_HEIGHT = 12
MAX = 255
SLIDER_COLORS = {
    "bordercolor": "#111159",
    "backgroundcolor": "#334455",
    "linecolor": "yellow"}


class MultiValueSlider(QtWidgets.QWidget):
    valuesChanged = QtCore.Signal()

    def __init__(self, colors=None, parent=None):
        super().__init__(parent)
        self.slider = _Slider(colors or SLIDER_COLORS.copy())
        self.handler = _Handler()
        self.handler.setFixedSize(SLIDER_HEIGHT, SLIDER_HEIGHT)
        self.handler.startHandeling.connect(self.start_handeling)
        self.handler.endHandeling.connect(self.end_handeling)
        self.handler.handled.connect(self.handled)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.handler)
        self._buffer = None

    @property
    def values(self):
        return self.slider.values

    def set_values(self, values):
        self._buffer = values
        self.slider.values = values

    def start_handeling(self):
        self._buffer = self.slider.values[:]

    def end_handeling(self):
        self._buffer = None

    def handled(self, offset):
        self._buffer = [v - offset for v in self._buffer]
        self.slider.values = [max([min([v, MAX]), 0]) for v in self._buffer]
        self.valuesChanged.emit()


class _Handler(QtWidgets.QWidget):
    handled = QtCore.Signal(int)
    startHandeling = QtCore.Signal()
    endHandeling = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pressed = False
        self.ghost = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.pressed = True
            self.ghost = event.position()
            self.startHandeling.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.pressed = False
            self.ghost = None
            self.endHandeling.emit()

    def mouseMoveEvent(self, event):
        if not self.ghost:
            return
        value = self.ghost.x() - event.position().x()
        func = math.ceil if value > 0 else math.floor
        self.handled.emit(int(func(value)))
        self.ghost = event.position()

    def sizeHint(self):
        return QtCore.QSize(25, 25)

    def enterEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.SizeHorCursor)

    def leaveEvent(self, event):
        QtWidgets.QApplication.restoreOverrideCursor()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.darkGray)
        painter.setPen(QtCore.Qt.transparent)

        romb = QtGui.QPolygonF()
        rect = self.rect()
        romb.append(QtCore.QPointF(rect.center().x(), 0))
        romb.append(QtCore.QPointF(rect.right(), rect.center().y()))
        romb.append(QtCore.QPointF(rect.center().x(), rect.bottom()))
        romb.append(QtCore.QPointF(0, rect.center().y()))
        painter.drawPolygon(romb)
        painter.end()


class _Slider(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)

    def __init__(self, colors=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(SLIDER_HEIGHT)
        self.colors = colors or get_colors()
        self.value_lines = []
        self._values = []

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values
        self.compute_shapes()
        self.repaint()

    def compute_shapes(self):
        self.value_lines = get_value_lines(self, self.values)

    def resizeEvent(self, _):
        self.compute_shapes()
        self.repaint()

    def paintEvent(self, _):
        if not self.value_lines:
            self.compute_shapes()
        # if any error appmaximum during the paint, all the application freeze
        # to avoid this error, the paint is placed under a global try
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            drawslider(painter, self, self.colors)
        except Exception:
            import traceback
            print(traceback.format_exc())
        finally:
            painter.end()


def drawslider(painter, slider, colors=None):
    colors = get_colors(colors)
    transparent = QtGui.QColor(0, 0, 0, 0)
    # draw background
    backgroundcolor = QtGui.QColor(colors['backgroundcolor'])
    pen = QtGui.QPen(transparent)
    brush = QtGui.QBrush(backgroundcolor)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawRect(slider.rect())
    # draw marks
    for value_line in slider.value_lines:
        pen.setWidthF((slider.width() / MAX) * 3)
        linecolor = QtGui.QColor(colors['linecolor'])
        linecolor.setAlpha(50)
        pen.setColor(linecolor)
        brush.setColor(transparent)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(value_line)
    # draw borderp
    pen.setWidth(2)
    bordercolor = QtGui.QColor(colors['bordercolor'])
    pen.setColor(bordercolor)
    brush.setColor(transparent)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawRect(slider.rect())


def get_value_line(slider, value):
    rect = slider.rect()
    left = value * (rect.width() / MAX)
    minimum = QtCore.QPoint(left, rect.top())
    maximum = QtCore.QPoint(left, rect.bottom())
    return QtCore.QLine(minimum, maximum)


def get_value_lines(slider, values):
    return [get_value_line(slider, value) for value in values]


def get_colors(colors):
    colorscopy = SLIDER_COLORS.copy()
    if colors is not None:
        colorscopy.update(colors)
    return colorscopy
