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
GAME_DATAS = cctx.initialize(GAMEDATAS_FOLDER)

from PyQt5 import QtWidgets
from scene_editor.highlighter import CoraxHighlighter, RULES

class SceneEditor(QtWidgets.QWidget):
    def __init__(self, scene_data, gamecontext, parent=None):
        super().__init__(parent=parent)
        self.tree = create_scene_outliner_tree(scene_datas)
        self.paintcontext = PaintContext(scene_datas)
        self.gamecontext = gamecontext

        self.scenewidget = SceneWidget(self.tree, gamecontext, self.paintcontext)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.scenewidget)

        self.model = OutlinerTreeModel(self.tree)
        self.outliner = OutlinerView()
        self.outliner.setModel(self.model)
        self.selection_model = self.outliner.selectionModel()
        self.selection_model.selectionChanged.connect(self.node_selected)

        self.dataeditor = QtWidgets.QPlainTextEdit()
        self.h = CoraxHighlighter(
            RULES["json"], document=self.dataeditor.document())

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.addWidget(self.outliner)
        self.hlayout.addWidget(self.dataeditor)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.addWidget(self.scroll)
        self.vlayout.addLayout(self.hlayout)

    def node_selected(self, selection, _):
        indexes = selection.indexes()
        data = self.model.getNode(indexes[0]).data
        text = data_to_plain_text(data)
        self.dataeditor.setPlainText(text)


if __name__ == "__main__":

    from scene_editor.tree import create_scene_outliner_tree
    from scene_editor.datas import data_to_plain_text
    from scene_editor.paint import PaintContext
    from scene_editor.outliner import OutlinerTreeModel, OutlinerView
    from scene_editor.scene import SceneWidget

    for scene in GAME_DATAS["scenes"]:
        if scene["name"] == GAME_DATAS["start_scene"]:
            filename = scene["file"]
    scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
    with open(scene_filepath, "r") as f:
        scene_datas = json.load(f)

    app = QtWidgets.QApplication([])

    window = SceneEditor(scene_datas, cctx)
    window.show()

    stylesheetpath = os.path.join(os.path.dirname(__file__), "..", "flatdark.css")
    stylesheet = ""
    with open(stylesheetpath, "r") as f:
        for line in f:
            stylesheet += line

    app.setStyleSheet(stylesheet)

    app.exec_()