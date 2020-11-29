
from functools import partial
from PyQt5 import QtCore, QtGui, QtWidgets


class FieldView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        emitter = partial(emit_spot_position, zone=Rect(150, 55, 400, 56))
        self.field = Field(Rect(0, 50, 1000, 500), 30, emitter=emit_spot_position, flow=1)
        self.timer = QtCore.QBasicTimer()
        self.timer.start(25, self)

    def timerEvent(self, event):
        self.field.next()
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.field.zone.left -= 10
            self.field.zone.right -= 10
        if event.key() == QtCore.Qt.Key_Right:
            self.field.zone.left += 10
            self.field.zone.right += 10

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 0)))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.drawRect(
            self.field.zone.left,
            self.field.zone.top,
            self.field.zone.width,
            self.field.zone.height)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        for spot in self.field.spots:
            painter.drawEllipse(spot.position[0], spot.position[1], 1, 1)
        painter.end()


app = QtWidgets.QApplication([])
window = FieldView()
window.show()
app.exec_()