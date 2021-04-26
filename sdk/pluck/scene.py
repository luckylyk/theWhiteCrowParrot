import json
from PyQt5 import QtWidgets, QtGui, QtCore

import corax.context as cctx

from pluck.paint import PaintContext, render_grid, render_cursor, render_handler
from pluck.highlighter import CoraxHighlighter, RULES
from pluck.data import data_sanity_check, tree_sanity_check, data_to_plain_text
from pluck.tree import tree_to_plaintext, get_scene, list_sounds, list_layers, list_zones, get_scene, create_scene_outliner_tree
from pluck.qtutils import get_image
from pluck.outliner import OutlinerTreeModel, OutlinerView


ZONE_TEMPLATE = """
zone selected: {0}

        {{
            "name": "unnamed",
            "type": "no_go",
            "affect": null,
            "zone": {0}
        }}

        {{
            "name": "unnamed",
            "type": "interaction",
            "scripts": null,
            "affect": null,
            "zone": {0}
        }}
"""


class SceneEditor(QtWidgets.QWidget):
    def __init__(self, scene_data, gamecontext, parent=None):
        super().__init__(parent=parent)
        self.tree = create_scene_outliner_tree(scene_data)
        self.paintcontext = PaintContext(scene_data)
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


class SceneWidget(QtWidgets.QWidget):
    def __init__(self, tree, coraxcontext, paintcontext, parent=None):
        super().__init__(parent=parent)
        self.paintcontext = paintcontext
        self.tree = tree
        self.coraxcontext = coraxcontext
        self.recompute_size()
        self.setMouseTracking(True)
        self.block_position = None
        self.block_position_backed_up = None
        self.is_handeling = False

    def mousePressEvent(self, event):
        if not self.block_position:
            return
        x, y = self.block_position
        zone = get_scene(self.tree).data["boundary"]
        if self.paintcontext.zone_contains_block_position(zone, x, y):
            self.block_position_backed_up = self.block_position
        self.is_handeling = True

    def mouseReleaseEvent(self, event):
        if not self.block_position_backed_up or not self.is_handeling:
            self.is_handeling = False
            self.block_position_backed_up = None
            self.repaint()
            return

        self.is_handeling = False
        x = min([self.block_position[0], self.block_position_backed_up[0]])
        y = min([self.block_position[1], self.block_position_backed_up[1]])
        x2 = max([self.block_position[0], self.block_position_backed_up[0]])
        y2 = max([self.block_position[1], self.block_position_backed_up[1]])
        mesagebox = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.NoIcon,
            "Zone selected:",
            ZONE_TEMPLATE.format([int(n) for n in [x, y, x2 + 1, y2 + 1]]),
            QtWidgets.QMessageBox.Ok)
        mesagebox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        mesagebox.exec_()
        self.repaint()

    def mouseMoveEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.block_position = self.paintcontext.block_position(x, y)
        self.repaint()

    def recompute_size(self):
        scene_data = self.tree.children[0].data
        w, h = scene_data["boundary"][2], scene_data["boundary"][3]
        w = self.paintcontext.relatives(w) + (2 * self.paintcontext.extra_zone)
        h = self.paintcontext.relatives(h) + (2 * self.paintcontext.extra_zone)
        self.setFixedSize(w, h)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.recompute_size()
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            self.paint(painter)
            painter.end()
        except:
            raise

    def paint(self, painter):
        scene_data = self.tree.children[0].data
        self.tree.children[0].render(painter, self.paintcontext)
        nodes = [
            n for l in list_layers(self.tree)
            for n in l.flat() if l.has_to_be_rendered]

        for node in nodes:
            if node.visible:
                node.render(painter, self.paintcontext)
        render_grid(
            painter,
            self.rect(),
            self.coraxcontext.BLOCK_SIZE,
            self.paintcontext)
        for sound in list_sounds(self.tree):
            if sound.has_to_be_rendered:
                sound.render(painter, self.paintcontext)
        for zone in list_zones(self.tree):
            if zone.has_to_be_rendered:
                zone.render(painter, self.paintcontext)

        if self.is_handeling is True and self.block_position_backed_up:
            bi, bo = self.block_position, self.block_position_backed_up
            render_handler(painter, bi, bo, self.paintcontext)
        elif self.block_position is not None:
            zone = get_scene(self.tree).data["boundary"]
            x, y = self.block_position
            if self.paintcontext.zone_contains_block_position(zone, x, y):
                render_cursor(painter, self.block_position, self.paintcontext)