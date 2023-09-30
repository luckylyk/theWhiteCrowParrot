import math
import random
from PySide2 import QtWidgets, QtGui, QtCore


class PathTester(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.display = PathDisplay()
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
        self.generate = QtWidgets.QPushButton('Generate')
        self.generate.released.connect(self.call_generate)

        options = QtWidgets.QHBoxLayout()
        options.addWidget(self.tension)
        options.addWidget(self.duration)
        options.addWidget(self.generate)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addLayout(options)

    def call_generate(self):
        self.display.start_point = random.randint(0, 600), random.randint(0, 600)
        self.display.end_point = random.randint(0, 600), random.randint(0, 600)
        self.update_canvas()

    def update_canvas(self):
        self.display.tension = self.tension.value()
        self.display.duration = self.duration.value()
        self.display.repaint()


class PathDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.tension = 15
        self.duration = 45
        self.clicked = None

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_point = event.pos().x(), event.pos().y()
            self.clicked = QtCore.Qt.LeftButton
            self.repaint()
        if event.button() == QtCore.Qt.RightButton:
            self.end_point = event.pos().x(), event.pos().y()
            self.clicked = QtCore.Qt.RightButton
            self.repaint()

    def mouseMoveEvent(self, event):
        if self.clicked == QtCore.Qt.LeftButton:
            self.start_point = event.pos().x(), event.pos().y()
            self.repaint()
        if self.clicked == QtCore.Qt.RightButton:
            self.end_point = event.pos().x(), event.pos().y()
            self.repaint()

    def mouseReleaseEvent(self, event):
        self.clicked = None

    def paintEvent(self, _):
        painter = QtGui.QPainter(self)
        painter.drawRect(self.rect())
        if not self.start_point or not self.end_point:
            painter.end()
            return

        buff = None
        points, cvs = get_path(self.start_point, self.end_point, self.tension)
        for point in points:
            if buff is None:
                buff = point
                continue
            painter.drawLine(QtCore.QPointF(*buff), QtCore.QPointF(*point))
            buff = point

        pen = QtGui.QPen(QtGui.QColor('orange'))
        pen.setWidth(3)
        painter.setPen(pen)
        for point in cvs:
            painter.drawPoint(QtCore.QPointF(*point))
            continue

        pen = QtGui.QPen(QtCore.Qt.blue)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPoint(QtCore.QPointF(*self.end_point))
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawPoint(QtCore.QPointF(*self.start_point))
        painter.end()


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
        start_point, control_points, end_point, output_point_number):
    control_points.append(end_point)
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
    return [start_point] + output_points + [end_point]


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    t = PathTester()
    t.show()
    app.exec_()