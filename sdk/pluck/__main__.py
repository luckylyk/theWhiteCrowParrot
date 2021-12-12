# generate environment
import os
import sys


HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
SDK_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)
sys.path.append(SDK_FOLDER)

# initialize project
import corax.context as cctx
from pluck.context import MockArguments

GAMEDATA_FOLDER = sys.argv[1]
MockArguments.game_root = os.path.abspath(GAMEDATA_FOLDER)
GAME_DATA = cctx.initialize(MockArguments)


if __name__ == "__main__":
    from PySide6 import QtWidgets
    from pluck.css import get_css
    from pluck.main import PluckMainWindow
    app = QtWidgets.QApplication([])

    window = PluckMainWindow()
    window.set_workspace(os.path.realpath(GAMEDATA_FOLDER))
    window.show()

    stylesheet = get_css("flatdark.css")
    app.setStyleSheet(stylesheet)
    app.exec()

