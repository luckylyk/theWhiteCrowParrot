# generate environment
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
SDK_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)
sys.path.append(SDK_FOLDER)

# initialize project
import corax.context as cctx
GAMEDATA_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_DATA = cctx.initialize(["", GAMEDATA_FOLDER])


if __name__ == "__main__":
    from PyQt5 import QtWidgets
    from pluck.css import get_css
    from pluck.main import PluckMainWindow
    app = QtWidgets.QApplication([])

    window = PluckMainWindow()
    window.set_workspace(os.path.realpath(GAMEDATA_FOLDER))
    window.show()

    stylesheet = get_css("flatdark.css")
    app.setStyleSheet(stylesheet)
    app.exec_()