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
GAMEDATAS_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_DATAS = cctx.initialize(["", GAMEDATAS_FOLDER])


if __name__ == "__main__":
    from PyQt5 import QtWidgets, QtCore, QtGui
    from pluck.scene import SceneEditor
    from pluck.css import get_css


    for scene in GAME_DATAS["scenes"]:
        if scene["name"] == GAME_DATAS["start_scene"]:
            filename = scene["file"]
    scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
    with open(scene_filepath, "r") as f:
        scene_datas = json.load(f)

    app = QtWidgets.QApplication([])

    window = SceneEditor(scene_datas, cctx)
    window.show()

    stylesheet = get_css("flatdark.css")
    app.setStyleSheet(stylesheet)
    app.exec_()