from PyQt5 import QtGui, QtCore, QtWidgets


SLIDER_HEIGHT = 22
SLIDER_COLORS = {
    "bordercolor": "#111159",
    "backgroundcolor.filled": "#777777",
    "backgroundcolor.empty": "#334455",
    "framelinecolor": "#FFCC33",
    "frameplayrangecolor": "#AA8800"}


class Slider(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.setFixedHeight(SLIDER_HEIGHT)
        self._minimum = None
        self._maximum = None
        self._start = None
        self._end = None
        self._value = None
        self._maximum_settable_value = None
        self._mouse_lb_is_pressed = False
        self._mouse_rb_edit_mode = None

        self.filled_rect = None
        self.value_line = None
        self.start_line = None
        self.end_line = None

    @property
    def minimum(self):
        return self._minimum

    @minimum.setter
    def minimum(self, value):
        if self._value is None:
           self._value = value
        if self._start is None:
            self._start = value
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
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value
        self.compute_shapes()
        self.repaint()

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value
        self.compute_shapes()
        self.repaint()

    @property
    def value(self):
        return self._value

    @property
    def position(self):
        if self._value is None:
            return None
        return self._value - self._minimum - 1

    @value.setter
    def value(self, value):
        if self._mouse_lb_is_pressed is True:
            return
        self._value = value
        self.compute_shapes()
        self.repaint()
        self.valueChanged.emit(value)

    @property
    def maximum_settable_value(self):
        return self._maximum_settable_value

    @maximum_settable_value.setter
    def maximum_settable_value(self, value):
        if self._end is None or self._end == self._maximum_settable_value:
            self._end = value
        self._maximum_settable_value = value
        self.compute_shapes()
        self.repaint()

    def compute_shapes(self):
        values = [self.minimum, self.maximum, self.maximum_settable_value]
        if all(v is not None for v in values) is False:
            return
        self.filled_rect = get_filled_rect(self)
        self.value_line = get_value_line(self, self.value)
        self.start_line = get_value_line(self, self.start)
        self.end_line = get_value_line(self, self.end)

    def mousePressEvent(self, event):
        if self._value is None or self._maximum_settable_value is None:
            return
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_lb_is_pressed = True
        elif event.button() == QtCore.Qt.RightButton:
            self._mouse_rb_edit_mode = self.get_mouse_rb_edit_mode(event.pos())
        self.set_value_from_point(event.pos())

    def resizeEvent(self, _):
        self.compute_shapes()
        self.repaint()

    def mouseMoveEvent(self, event):
        if self._value is None:
            return
        if self._mouse_lb_is_pressed is True:
            self.set_value_from_point(event.pos())
        if self._mouse_rb_edit_mode is not None:
            self.set_value_from_point(event.pos())

    def mouseReleaseEvent(self, event):
        self._mouse_lb_is_pressed = False
        self._mouse_rb_edit_mode = None

    def get_mouse_rb_edit_mode(self, point):
        value = get_value_from_point(self, point)
        if abs(self.maximum - value) > abs(self.minimum - value):
            return 'start'
        return 'end'

    def set_value_from_point(self, point):
        if not all([self.filled_rect, self.value_line]):
            self.compute_shapes()
        if not self.rect().bottom() < point.y() < self.rect().top():
            point.setY(self.rect().top())
        if not self.rect().contains(point):
            return
        value = get_value_from_point(self, point)
        if self._mouse_lb_is_pressed is True or self._mouse_rb_edit_mode:
            self._value = value
        if self._mouse_rb_edit_mode == 'start':
            if value < self._end:
                self._start = value
        elif self._mouse_rb_edit_mode == 'end':
            if value > self._start:
                self._end = get_value_from_point(self, point)
        self.compute_shapes()
        self.repaint()
        self.valueChanged.emit(self._value)

    def paintEvent(self, event):
        if not all([self.filled_rect, self.value_line]):
            self.compute_shapes()
        # if any error append during the paint, all the application freeze
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
    # draw filled
    if slider.filled_rect:
        backgroundcolor = QtGui.QColor(colors['backgroundcolor.filled'])
        pen.setColor(transparent)
        brush.setColor(backgroundcolor)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawRect(slider.filled_rect)
    # draw start/end
    if slider.start_line and slider.end_line:
        pen.setWidth(3)
        linecolor = QtGui.QColor(colors['frameplayrangecolor'])
        pen.setColor(linecolor)
        brush.setColor(transparent)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(slider.start_line)
        painter.drawLine(slider.end_line)
    # draw current
    if slider.value_line:
        pen.setWidth(10)
        linecolor = QtGui.QColor(colors['framelinecolor'])
        pen.setColor(linecolor)
        brush.setColor(transparent)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(slider.value_line)
    # draw border
    pen.setWidth(5)
    bordercolor = QtGui.QColor(colors['bordercolor'])
    pen.setColor(bordercolor)
    brush.setColor(transparent)
    painter.setBrush(brush)
    painter.setPen(pen)
    painter.drawRect(slider.rect())


def get_value_line(slider, value):
    rect = slider.rect()
    horizontal_divisor = float(slider.maximum - slider.minimum) or 1
    horizontal_unit_size = rect.width() / horizontal_divisor
    left = (value - slider.minimum) * horizontal_unit_size
    start = QtCore.QPoint(left, rect.top())
    end = QtCore.QPoint(left, rect.bottom())
    return QtCore.QLine(start, end)


def get_filled_rect(slider):
    if slider.maximum_settable_value == slider.minimum:
        return None
    rect = slider.rect()
    horizontal_divisor = float(slider.maximum - slider.minimum) or 1
    horizontal_unit_size = rect.width() / horizontal_divisor
    width = (slider.maximum_settable_value - slider.minimum) * horizontal_unit_size
    return QtCore.QRectF(rect.left(), rect.top(), width, rect.height())


def get_value_from_point(slider, point):
    if slider.filled_rect is None or not slider.filled_rect.contains(point):
        return slider.maximum_settable_value
    horizontal_divisor = float(slider.maximum - slider.minimum)
    horizontal_unit_size = slider.rect().width() / horizontal_divisor
    value = 0
    x = 0
    while x < point.x():
        value += 1
        x += horizontal_unit_size
    return value + slider.minimum


def get_colors(colors):
    colorscopy = SLIDER_COLORS.copy()
    if colors is not None:
        colorscopy.update(colors)
    return colorscopy
