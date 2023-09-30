import math
import itertools
from PySide2 import QtWidgets, QtGui, QtCore


class PathTester(QtWidgets.QWidget):
    def __init__(self, points, parent=None):
        super().__init__(parent)
        self.display = PathDisplay(points)
        self.tension = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.tension.setMinimum(10)
        self.tension.setMaximum(120)
        self.tension.setValue(15)
        self.tension.valueChanged.connect(self.update_canvas)
        self.duration = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.duration.setMinimum(10)
        self.duration.setMaximum(120)
        self.duration.setValue(45)
        self.duration.valueChanged.connect(self.update_canvas)
        self.generate = QtWidgets.QPushButton('print')
        self.generate.released.connect(self.call_generate)
        self.reset = QtWidgets.QPushButton('reset')
        self.reset.released.connect(self.call_reset)

        options = QtWidgets.QHBoxLayout()
        options.addWidget(self.generate)
        options.addWidget(self.reset)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addLayout(options)
        self.timer = QtCore.QBasicTimer()
        self.timer.start(33, self)

    def timerEvent(self, _):
        self.display.ev()

    def call_generate(self):
        print([(
            self.display.rect().center().x() - point[0],
            self.display.rect().center().y() - point[1])
            for point in self.display.points])

    def call_reset(self):
        self.display.points = []
        self.update_canvas()

    def update_canvas(self):
        self.display.tension = self.tension.value()
        self.display.duration = self.duration.value()
        self.display.repaint()


class PathDisplay(QtWidgets.QWidget):
    def __init__(self, points, parent=None):
        super().__init__(parent)
        self.center = self.rect().center()
        self.clicked = None
        self.cv = points
        self.points = bezier_interpolation(points, 50)[:-1]
        self.point = None
        self.path = []
        self.index_iterator = itertools.cycle(list(range(len(self.points))))
        self.buffer = []

    def ev(self):
        self.buffer.append(self.center)
        self.buffer = self.buffer[-20:]
        x = sum(p.x() for p in self.buffer) / len(self.buffer)
        y = sum(p.y() for p in self.buffer) / len(self.buffer)
        index = next(self.index_iterator)
        self.point = (self.points[index][0] + x), (self.points[index][1] + y)
        # self.buffer = point
        self.repaint()

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def mouseMoveEvent(self, event):
        self.center = event.pos()
        self.repaint()

    def paintEvent(self, _):
        painter = QtGui.QPainter(self)
        painter.drawRect(self.rect())

        painter.drawPoint(self.rect().center())

        points = [
            (self.center.x() + p[0], self.center.y() + p[1])
            for p in self.cv]
        bpoints = bezier_interpolation(points, len(points) * 5)
        buff = None
        for point in bpoints:
            if buff is None:
                buff = point
                continue
            painter.drawLine(QtCore.QPointF(*buff), QtCore.QPointF(*point))
            buff = point

        pen = QtGui.QPen(QtGui.QColor('orange'))
        pen.setWidth(3)
        painter.setPen(pen)
        for point in points:
            painter.drawPoint(QtCore.QPointF(*point))
            continue

        if self.point:
            pen = QtGui.QPen(QtGui.QColor('red'))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.drawPoint(QtCore.QPointF(*self.point))


def distance_2d(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dy, dx)
    return math.degrees(angle)


def get_vector(degree, length):
    radian = math.radians(degree)
    x = length * math.cos(radian)
    y = length * math.sin(radian)
    return x, y


def sum_points(*points):
    return sum(p[0] for p in points), sum(p[1] for p in points)


PATH = [
    (270, 50),
    (230, 17),
    (210, 10),
    (180, 5),
    (130, 3),
    (100, 2.5),
    (60, 2)
]


def get_path(start_point, end_point, iterations):
    original_distance = distance_2d(start_point, end_point)
    original_angle = get_angle(start_point, end_point)
    points = [start_point]
    reverse = start_point[0] < end_point[0]
    cvs = [start_point]
    for angle, division in PATH:
        oangle = original_angle - angle if reverse else original_angle + angle
        offset = get_vector(oangle, (original_distance / division) if division else 0)
        cvs.append(sum_points(start_point, offset))
    points = bezier_interpolation(start_point, cvs, end_point, iterations)
    return points, cvs


def bezier_interpolation(
        control_points, output_point_number):
    step = 1.0 / (output_point_number - 1)
    output_points = []

    for t in range(output_point_number):
        t_value = t * step
        one_minus_t = 1.0 - t_value
        points = control_points[:]

        while len(points) > 1:
            next_points = []
            for i in range(len(points) - 1):
                x = points[i][0] * one_minus_t + points[i + 1][0] * t_value
                y = points[i][1] * one_minus_t + points[i + 1][1] * t_value
                next_points.append((x, y))
            points = next_points
        output_points.append(points[0])
    return output_points


if __name__ == '__main__':

    points1 = [(0, 0), (48, -1), (102, -8), (120, -25), (128, -44), (128, -75), (113, -90), (93, -63), (88, -30), (83, -16), (38, 28), (0, 35)]
    points2 = list(reversed(list((-p[0], p[1]) for p in points1)))
    points = points1 + points2
    app = QtWidgets.QApplication([])
    t = PathTester(points)
    t.show()
    app.exec_()