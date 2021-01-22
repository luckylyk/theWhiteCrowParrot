from PyQt5 import QtWidgets, QtCore

import os
import sys
HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
print(os.path.realpath(MAIN_FOLDER))
sys.path.append(MAIN_FOLDER)
import whitecrow.constants
whitecrow.constants.populate()
from whitecrow.constants import ANIMATION_FOLDER


class SceneWidget(QtWidgets.QWidget):
    def __init__(self, scene_datas, parent=None):
        super().__init__(parent=parent)
        self.scene_datas = scene_datas
        self.images = load_images(self.scene_datas)

    def paintEvent(self, event):
        painter = QtCore.QPaint()
        try:
            painter.begin(self)
            self.paint(painter)
            painter.end()
        except:
            raise

    def paint(self, painter):
        pass
