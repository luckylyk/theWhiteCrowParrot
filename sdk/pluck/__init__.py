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

from PyQt5 import QtWidgets, QtCore, QtGui
from pluck.highlighter import CoraxHighlighter, RULES
from pluck.datas import data_sanity_check, tree_sanity_check
from pluck.tree import tree_to_plaintext, get_scene
from pluck.qtutils import get_image


class SceneEditor(QtWidgets.QWidget):
    def __init__(self, scene_data, gamecontext, parent=None):
        super().__init__(parent=parent)
        self.tree = create_scene_outliner_tree(scene_datas)
        self.paintcontext = PaintContext(scene_datas)
        self.gamecontext = gamecontext

        self.scenewidget = SceneWidget(self.tree, gamecontext, self.paintcontext)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.horizontalScrollBar().setSliderPosition(50)
        self.scroll.verticalScrollBar().setSliderPosition(50)
        self.scroll.setWidget(self.scenewidget)

        self.model = OutlinerTreeModel(self.tree)
        self.outliner = OutlinerView()
        self.outliner.setModel(self.model)
        self.outliner.expandAll()
        self.model.dataChanged.connect(self.update_graphics)
        self.selection_model = self.outliner.selectionModel()
        self.selection_model.selectionChanged.connect(self.node_selected)

        nowrap = QtGui.QTextOption.NoWrap
        self.dataeditor = QtWidgets.QPlainTextEdit()
        self.dataeditor.setWordWrapMode(nowrap)
        self.dataeditor.textChanged.connect(self.update_data)
        document = self.dataeditor.document()
        self.h = CoraxHighlighter(RULES["json"], document=document)

        self.image = QtWidgets.QLabel()
        self.image.setFixedSize(400, 400)

        self.data_traceback = QtWidgets.QLabel()
        self.data_traceback2 = QtWidgets.QLabel()

        self.json_editor = QtWidgets.QPlainTextEdit()
        self.json_editor.setWordWrapMode(nowrap)
        document = self.json_editor.document()
        self.json_editor.textChanged.connect(self.json_edited)
        self.h2 = CoraxHighlighter(RULES["json"], document=document)

        self.vlayout_widget = QtWidgets.QWidget()
        self.vlayout = QtWidgets.QVBoxLayout(self.vlayout_widget)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.addWidget(self.dataeditor)
        self.vlayout.addWidget(self.data_traceback)

        self.vlayout2_widget = QtWidgets.QWidget()
        self.vlayout2 = QtWidgets.QVBoxLayout(self.vlayout2_widget)
        self.vlayout2.setContentsMargins(0, 0, 0, 0)
        self.vlayout2.addWidget(self.json_editor)
        self.vlayout2.addWidget(self.data_traceback2)

        self.hsplitter = QtWidgets.QSplitter()
        self.hsplitter.addWidget(self.outliner)
        self.hsplitter.addWidget(self.vlayout_widget)

        self.hwidget = QtWidgets.QWidget()
        self.hlayout = QtWidgets.QHBoxLayout(self.hwidget)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.addWidget(self.hsplitter)
        self.hlayout.addWidget(self.image)

        self.vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.vsplitter.addWidget(self.scroll)
        self.vsplitter.addWidget(self.hwidget)

        self.hsplitter2 = QtWidgets.QSplitter()
        self.hsplitter2.addWidget(self.vsplitter)
        self.hsplitter2.addWidget(self.vlayout2_widget)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.hsplitter2)
        self.json_editor.setPlainText(tree_to_plaintext(self.tree))

    def update_data(self, *useless_signal_args):
        self.outliner.setEnabled(True)
        self.data_traceback.setStyleSheet("")
        text = self.dataeditor.toPlainText()
        if text == "":
            self.data_traceback.setText("")
            self.image.setPixmap(QtGui.QPixmap())
            return
        try:
            data = json.loads(text)
            data_sanity_check(data)
            node = self.selected_node()
            node.data = data
            self.scenewidget.repaint()
            self.data_traceback.setText("")
            if data.get("file"):
                image = get_image(data)
                if image:
                    s = self.image.size()
                    r = QtCore.Qt.KeepAspectRatio
                    t = QtCore.Qt.SmoothTransformation
                    pixmap = QtGui.QPixmap.fromImage(image).scaled(s, r, t)
                    self.image.setPixmap(pixmap)
            self.json_editor.setPlainText(tree_to_plaintext(self.tree))
        except json.decoder.JSONDecodeError:
            self.data_traceback.setText("JSon Syntax error")
            self.data_traceback.setStyleSheet("background-color:red")
            self.outliner.setEnabled(False)
        except Exception as e:
            self.data_traceback.setText(str(e))
            self.data_traceback.setStyleSheet("background-color:red")
            self.outliner.setEnabled(False)

    def json_edited(self, *useless_args):
        if not self.json_editor.hasFocus():
            return
        text = self.json_editor.toPlainText()
        try:
            data = json.loads(text)
            tree = create_scene_outliner_tree(data)
            tree_sanity_check(tree)
        except json.decoder.JSONDecodeError:
            self.data_traceback2.setText("JSon Syntax error")
            self.data_traceback2.setStyleSheet("background-color:red")
            return
        except Exception as e:
            self.data_traceback2.setText(str(e))
            self.data_traceback2.setStyleSheet("background-color:red")
            return

        self.data_traceback2.setText("")
        self.data_traceback2.setStyleSheet("")
        self.tree = tree
        self.scenewidget.tree = tree
        self.model.set_tree(tree)
        self.outliner.expandAll()
        self.scenewidget.recompute_size()
        self.scenewidget.repaint()

    def update_graphics(self, *useless_signal_args):
        self.scenewidget.repaint()

    def selected_node(self):
        indexes = self.selection_model.selectedIndexes()
        if not indexes:
            return
        return self.model.getNode(indexes[0])

    def node_selected(self, selection, _):
        indexes = selection.indexes()
        data = self.model.getNode(indexes[0]).data
        if data is None:
            self.dataeditor.setEnabled(False)
            self.dataeditor.setPlainText("")
            return
        self.dataeditor.setEnabled(True)
        text = data_to_plain_text(data)
        self.dataeditor.setPlainText(text)


if __name__ == "__main__":

    from pluck.tree import create_scene_outliner_tree
    from pluck.datas import data_to_plain_text
    from pluck.paint import PaintContext
    from pluck.outliner import OutlinerTreeModel, OutlinerView
    from pluck.scene import SceneWidget

    for scene in GAME_DATAS["scenes"]:
        if scene["name"] == GAME_DATAS["start_scene"]:
            filename = scene["file"]
    scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
    with open(scene_filepath, "r") as f:
        scene_datas = json.load(f)

    app = QtWidgets.QApplication([])

    window = SceneEditor(scene_datas, cctx)
    window.show()

    stylesheetpath = os.path.join(os.path.dirname(__file__), "flatdark.css")
    stylesheet = ""
    with open(stylesheetpath, "r") as f:
        for line in f:
            stylesheet += line

    app.setStyleSheet(stylesheet)

    app.exec_()