from PyQt5 import QtGui, QtCore, QtWidgets


SLIDER_HEIGHT = 22
SLIDER_COLORS = {
    "bordercolor": "#111159",
    "backgroundcolor.filled": "#777777",
    "backgroundcolor.empty": "#334455",
    "framelinecolor": "#FFCC33",
    "markercolor": "red",
    "frameplayrangecolor": "#AA8800"}


class Slider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(SLIDER_HEIGHT)
        self._minimum = None
        self._maximum = None
        self._value = None
        self._mouse_lb_is_pressed = False
        self.value_line = None
        self.marks = []

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        self._minimum = value
        self.compute_shapes()
        self.repaint()

    @property
    def maximum(self):
        return self._maximum

    @maximum.setter
    def maximum(self, value):
        self._maximum = value
        self.compute_shapes()
        self.repaint()

    @property
    def value(self):
        return self._value or 0

    @value.setter
    def value(self, value):
        if self._mouse_lb_is_pressed is True:
            return
        self._value = value
        self.compute_shapes()
        self.repaint()
        self.valueChanged.emit(value)

    @property
    def marks(self):
        return self._marks

    @marks.setter
    def marks(self, marks):
        self._marks = marks
        self.compute_shapes()
        self.repaint()

    def compute_shapes(self):
        if None in [self.minimum, self.maximum]:
            return
        self.value_line = get_value_line(self, self.value)
        self.mark_lines = get_mark_lines(self, self.marks)

    def mousePressEvent(self, event):
        if self._value is None:
            return
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_lb_is_pressed = True
        self.set_value_from_point(event.pos())

    def resizeEvent(self, _):
        self.compute_shapes()
        self.repaint()

    def mouseMoveEvent(self, event):
        if self._value is None:
            return
        if self._mouse_lb_is_pressed is True:
            self.set_value_from_point(event.pos())

    def mouseReleaseEvent(self, _):
        self._mouse_lb_is_pressed = False

    def set_value_from_point(self, point):
        if not self.value_line:
            self.compute_shapes()
        if not self.rect().bottom() < point.y() < self.rect().top():
            point.setY(self.rect().top())
        if not self.rect().contains(point):
            return
        value = get_value_from_point(self, point)
        if self._mouse_lb_is_pressed:
            self._value = value
        self.compute_shapes()
        self.repaint()
        self.valueChanged.emit(self._value)

    def paintEvent(self, _):
        if not self.value_line:
            self.compute_shapes()
        # if any error appmaximum during the paint, all the application freeze
        # to avoid this error, the paint is placed under a global try
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            drawslider(painter, self)
        except Exception:
            import traceback
            print(traceback.format_exc())
        finally:
            painter.end()


def drawslider(painter, slider, colors=None):
    colors = get_colors(colors)
    transparent = QtGui.QColor(0, 0, 0, 0)
    # draw background
    backgroundcolor = QtGui.QColor(colors['backgroundcolor.empty'])
    pen = QtGui.QPen(transparent)
    brush = QtGui.QBrush(backgroundcolor)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawRect(slider.rect())
    # draw marks
    for mark_line in slider.mark_lines:
        pen.setWidth(10)
        linecolor = QtGui.QColor(colors['markercolor'])
        pen.setColor(linecolor)
        brush.setColor(transparent)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(mark_line)
    # draw current
    if slider.value_line:
        pen.setWidth(10)
        linecolor = QtGui.QColor(colors['framelinecolor'])
        pen.setColor(linecolor)
        brush.setColor(transparent)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(slider.value_line)
    # draw borderp
    pen.setWidth(5)
    bordercolor = QtGui.QColor(colors['bordercolor'])
    pen.setColor(bordercolor)
    brush.setColor(transparent)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawRect(slider.rect())


def get_value_line(slider, value):
    rect = slider.rect()
    horizontal_divisor = float(slider.maximum - slider.minimum) - 1 or 1
    horizontal_unit_size = rect.width() / horizontal_divisor
    left = (value - slider.minimum) * horizontal_unit_size
    minimum = QtCore.QPoint(left, rect.top())
    maximum = QtCore.QPoint(left, rect.bottom())
    return QtCore.QLine(minimum, maximum)


def get_mark_lines(slider, marks):
    return [get_value_line(slider, mark) for mark in marks]


def get_value_from_point(slider, point):
    if slider.maximum - slider.minimum <= 1:
        return slider.minimum
    horizontal_divisor = float(slider.maximum - slider.minimum) - 1 or 1
    horizontal_unit_size = slider.rect().width() / horizontal_divisor
    value = 0
    x = 0
    while x < point.x():
        value += 1
        x += horizontal_unit_size
    # If pointer is closer to previous value, we set the value to previous one.
    if (x - point.x() > point.x() - (x - horizontal_unit_size)):
        value -= 1
    return value + slider.minimum


def get_colors(colors):
    colorscopy = SLIDER_COLORS.copy()
    if colors is not None:
        colorscopy.update(colors)
    return colorscopy
