from PyQt5 import QtWidgets
import krita


class MyDocker(QtWidgets.DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Docker")

    def canvasChanged(self, canvas):
        pass
