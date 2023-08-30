
from functools import partial
import json

from PySide6 import QtWidgets, QtGui, QtCore
import corax.context as cctx

from pluck.dialog import CreateOnSceneDialog
from pluck.field import (
    IntField, StrField, TriggerField, InteractorField, ZoneField, OrderField,
    SoundFileField, SoundFilesField, StrArrayField, FloatField, FileField,
    IntVectorField, BoolField, ColorField, FieldPanel)
from pluck.highlighter import CoraxHighlighter, RULES
from pluck.outliner import OutlinerTreeModel, OutlinerView
from pluck.qtutils import get_icon
from pluck.paint import PaintContext
from pluck.ressource import (
    LAYER_FILENAME, PLAYER_PLACEHOLDER_FILENAME, SET_ANIMATED_FILENAME,
    SET_STATIC_FILENAME, load_json)
from pluck.sanity import tree_sanity_check
from pluck.sceneelement import SceneElementDialog
from pluck.scenewidget import SceneWidget
from pluck.sound import CreateSoundDialog
from pluck.tree import (
    tree_to_plaintext, create_scene_outliner_tree, clear_tree_selection)
from pluck.zone import CreateZoneDialog


FIELDS = {
    "scene": {
        "name": StrField,
        "background_color": ColorField,
        "boundary": ZoneField,
        # "soft_boundaries": [],
        "target_offset": IntVectorField,
    },
    "music": {
        "name": StrField,
        "file": SoundFileField,
        "channel": IntField,
        "falloff": IntField,
        "listener": InteractorField,
        "zone": ZoneField,
    },
    "ambiance": {
        "name": StrField,
        "file": SoundFileField,
        "channel": IntField,
        "falloff": IntField,
        "listener": InteractorField,
        "zone": ZoneField,
    },
    "sfx_sound_collection": {
        "name": StrField,
        "files": SoundFilesField,
        "channel": IntField,
        "falloff": IntField,
        "order": OrderField,
        "trigger": TriggerField,
        "zone": ZoneField,
        "emitter": InteractorField
    },
    "sfx_sound": {
        "name": StrField,
        "file": SoundFileField,
        "channel": IntField,
        "falloff": IntField,
        "trigger": TriggerField,
        "zone": ZoneField,
        "emitter": InteractorField
    },
    "no_go": {
        "name": StrField,
        "affect": StrArrayField,
        "zone": ZoneField
    },
    "interaction": {
        "name": StrField,
        "affect": StrArrayField,
        "scripts": StrArrayField,
        "zone": ZoneField
    },
    "event_zone": {
        "name": StrField,
        "affect": InteractorField,
        "events": StrArrayField,
        "zone": ZoneField,
        "target": StrField,
        "trigger": StrField
    },
    "collider": {
        "name": StrField,
        "affect": InteractorField,
        "scripts": StrArrayField,
        "zone": ZoneField,
        "event": StrField,
        "hitmaps": StrArrayField,
    },
    "relationship": {
        "name": StrField,
        "enable": BoolField,
        "subject": InteractorField,
        "target": InteractorField,
        "relationship": FileField,
        "zone": ZoneField
    },
    "layer": {
        "name": StrField,
        "deph": FloatField
    },
    "set_static": {
        "name": StrField,
        "file": FileField,
        "position": IntVectorField,
        "deph": FloatField,
        "visible": BoolField
    },
    "special_effects_emitter": {
        "name": StrField,
        "spritesheet_filename": FileField,
        "layers": StrArrayField,
        "alpha": IntField,
        "deph": FloatField,
        "repeat_delay": IntField,
        "persistents": BoolField,
        "animation_iteration_type": OrderField
    },
    "particles_system": {
        # "name": StrField,
        # "alpha": IntField,
        # "deph": FloatField,
        # "direction_options": {
        #         "rotation_range": -1,
        #         "speed": 10
        #     },
        # "emission_positions":  null,
        # "emission_zone":  null,
        # "flow": IntVectorField,
        # "shape_options": {
        #         "type": "square",
        #         "alpha": IntVectorField,
        #         "color": ColorField,
        #         "size": IntVectorField
        #     },
        # "spot_options": {
        #         "boundary_behavior": "bounce_on_boundary",
        #         "frequency": IntVectorField,
        #         "speed": [0.1, 0.2]
        #     },
        # "start_number": IntField,
        # "zone": ZoneField
    },
    "set_animated": {
        "name": StrField,
        "file": FileField,
        "position": IntVectorField,
        "alpha": IntField,
        "deph": FloatField
    },
    "player": {
        "name": StrField,
        "block_position": IntVectorField,
        "flip": BoolField
    },
    "npc": {
        "name": StrField,
        "block_position": IntVectorField,
        "flip": BoolField
    },
}


class SceneEditor(QtWidgets.QWidget):
    modified = QtCore.Signal()

    def __init__(self, scene_data, gamecontext, parent=None):
        super().__init__(parent=parent)
        self.is_modified = False
        self.block_modified_signal = False
        self.tree = create_scene_outliner_tree(scene_data)
        self.paintcontext = PaintContext()
        self.gamecontext = gamecontext

        self.scenewidget = SceneWidget()
        self.scenewidget.set_tree(self.tree)
        self.scenewidget.data = scene_data
        self.scenewidget.zoneSelected.connect(self.create_zonal)
        self.scenewidget.nodeSelected.connect(self.selected_from_view)

        self.toolbar = SceneContextToolbar()
        self.toolbar.zone.toggled.connect(self.scenewidget.set_zone_mode)
        self.toolbar.grid.toggled.connect(self.scenewidget.set_grid_visible)
        method = self.scenewidget.set_boundaries_visible
        self.toolbar.boundaries.toggled.connect(method)

        self.tree_toolbar = SceneTreeToolbar()
        method = partial(self.create_renderable_element, LAYER_FILENAME)
        self.tree_toolbar.layer.triggered.connect(method)
        fn = PLAYER_PLACEHOLDER_FILENAME
        method = partial(self.create_renderable_element, fn)
        self.tree_toolbar.player.triggered.connect(method)
        method = partial(self.create_renderable_element, SET_STATIC_FILENAME)
        self.tree_toolbar.static.triggered.connect(method)
        method = partial(self.create_renderable_element, SET_ANIMATED_FILENAME)
        self.tree_toolbar.animated.triggered.connect(method)

        self.model = OutlinerTreeModel(self.tree)
        self.outliner = OutlinerView()
        self.outliner.setModel(self.model)
        self.outliner.expandAll()
        self.model.dataChanged.connect(self.update_graphics)
        self.selection_model = self.outliner.selectionModel()
        method = self.selected_from_outliner
        self.selection_model.selectionChanged.connect(method)

        self.node_editor = NodeEditor()
        self.node_editor.edited.connect(self.field_value_changed)
        # self.node_editor.edited.connect(self.field_value_edited)

        self.tree_widget = QtWidgets.QWidget()
        self.tree_layout = QtWidgets.QVBoxLayout(self.tree_widget)
        self.tree_layout.setContentsMargins(0, 0, 0, 0)
        self.tree_layout.addWidget(self.tree_toolbar)
        self.tree_layout.addWidget(self.outliner)

        self.scene = QtWidgets.QWidget()
        self.scene_layout = QtWidgets.QVBoxLayout(self.scene)
        self.scene_layout.setContentsMargins(0, 0, 0, 0)
        self.scene_layout.addWidget(self.toolbar)
        self.scene_layout.addWidget(self.scenewidget)

        nowrap = QtGui.QTextOption.NoWrap
        self.json_editor = QtWidgets.QPlainTextEdit()
        self.json_editor.setWordWrapMode(nowrap)
        document = self.json_editor.document()
        self.json_editor.textChanged.connect(self.json_edited)
        self.h2 = CoraxHighlighter(RULES["json"], document=document)

        self.data_traceback = QtWidgets.QLabel()
        self.json_widget = QtWidgets.QWidget()
        self.jsont_layout = QtWidgets.QVBoxLayout(self.json_widget)
        self.jsont_layout.setContentsMargins(0, 0, 0, 0)
        self.jsont_layout.addWidget(self.json_editor)
        self.jsont_layout.addWidget(self.data_traceback)

        self.vsplitter_left = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.vsplitter_left.addWidget(self.scene)
        self.vsplitter_left.addWidget(self.json_widget)

        self.vsplitter_right = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.vsplitter_right.addWidget(self.tree_widget)
        self.vsplitter_right.addWidget(self.node_editor)

        self.hsplitter = QtWidgets.QSplitter()
        self.hsplitter.addWidget(self.vsplitter_left)
        self.hsplitter.addWidget(self.vsplitter_right)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.hsplitter)

        self.json_editor.setPlainText(tree_to_plaintext(self.tree))
        document.contentsChanged.connect(self.contents_changed)

        self.setMouseTracking(True)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.scenewidget.is_exploring = True
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.OpenHandCursor)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.scenewidget.is_exploring is True:
                QtWidgets.QApplication.restoreOverrideCursor()
            self.scenewidget.is_exploring = False

    def json_edited(self, *useless_args):
        if not self.json_editor.hasFocus():
            return
        text = self.json_editor.toPlainText()

        try:
            data = json.loads(text)
            tree = create_scene_outliner_tree(data)
            tree_sanity_check(tree)

        except json.decoder.JSONDecodeError:
            self.data_traceback.setText("JSon Syntax error")
            self.data_traceback.setStyleSheet("background-color:red")
            return

        except Exception as e:
            self.data_traceback.setText(str(e))
            self.data_traceback.setStyleSheet("background-color:red")
            return

        self.data_traceback.setText("")
        self.data_traceback.setStyleSheet("")
        self.update_tree(tree)

    def contents_changed(self):
        """
        Method to call when the content is changed. This indicate to the main
        application that the file need to be saved.
        """
        if self.is_modified or self.block_modified_signal is True:
            return
        self.is_modified = True
        print(self)
        self.modified.emit()

    def save(self, filename):
        if not self.is_modified:
            return
        with open(filename, "w") as f:
            f.write(str(self.json_editor.toPlainText()))
        self.is_modified = False

    def create_zonal(self, zone):
        dialog = CreateOnSceneDialog(zone)
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return

        match type_:=dialog.result:
            case "sounds":
                dialog = CreateSoundDialog(zone)
                result = dialog.exec()
                if result != QtWidgets.QDialog.Accepted:
                    return
                result = dialog.result

            case "zones":
                dialog = CreateZoneDialog(zone)
                result = dialog.exec()
                if result != QtWidgets.QDialog.Accepted:
                    return
                result = dialog.result

            case "soft_boundaries":
                result = [int(z * cctx.BLOCK_SIZE) for z in zone]

            case _:
                return

        data = json.loads(tree_to_plaintext(self.tree))
        data[type_].append(result)
        tree = create_scene_outliner_tree(data)
        self.update_tree(tree)
        self.contents_changed()
        self.blockSignals(True)
        self.json_editor.setPlainText(tree_to_plaintext(self.tree))
        self.blockSignals(False)

    def update_tree(self, tree):
        self.tree = tree
        self.scenewidget.tree = tree
        self.scenewidget.data = tree.children[0].data
        self.model.set_tree(tree)
        self.outliner.expandAll()
        self.scenewidget.repaint()

    def update_graphics(self, *useless_signal_args):
        self.scenewidget.repaint()

    def selected_node(self):
        indexes = self.selection_model.selectedIndexes()
        if not indexes:
            return
        return self.model.getNode(indexes[0])

    def field_value_changed(self, *_):
        if not (node:=self.node_editor.node):
            return
        node.data.update(self.node_editor.values)
        self.scenewidget.repaint()
        self.json_editor.setPlainText(tree_to_plaintext(self.tree))
        self.scenewidget.data = self.tree.children[0].data
        self.contents_changed()

    def selected_from_outliner(self, selection, _):
        self.block_modified_signal = True
        indexes = selection.indexes()
        node = self.model.getNode(indexes[0])
        clear_tree_selection(self.tree)
        node.selected = True
        self.block_modified_signal = False
        self.node_editor.set_node(node)

    def selected_from_view(self, node):
        _, first, *rows = node.nested_rows()
        index = self.model.index(first, 0)

        for row in rows:
            index = self.model.index(row, 0, index)

        self.selection_model.blockSignals(True)
        self.selection_model.clearSelection()
        flags = (
            QtCore.QItemSelectionModel.Select |
            QtCore.QItemSelectionModel.Rows)

        self.selection_model.select(index, flags)
        self.outliner.scrollTo(index)
        self.selection_model.blockSignals(False)
        self.node_editor.set_node(node)

    def create_renderable_element(self, filename):
        data = load_json(filename)
        dialog = SceneElementDialog(data)
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return


class SceneContextToolbar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zone = QtGui.QAction(get_icon("zone.png"), "", self)
        self.zone.setCheckable(True)
        self.grid = QtGui.QAction(get_icon("grid.png"), "", self)
        self.grid.setCheckable(True)
        self.grid.setChecked(True)
        self.boundaries = QtGui.QAction(get_icon("boundaries.png"), "", self)
        self.boundaries.setCheckable(True)
        self.boundaries.setChecked(True)

        self.addAction(self.zone)
        self.addAction(self.grid)
        self.addAction(self.boundaries)


class SceneTreeToolbar(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QtCore.QSize(18, 18))
        self.layer = QtGui.QAction(get_icon("layer.png"), "", self)
        self.player = QtGui.QAction(get_icon("player.png"), "", self)
        self.static = QtGui.QAction(get_icon("renderable.png"), "", self)
        self.animated = QtGui.QAction(get_icon("renderable.png"), "", self)

        self.addAction(self.layer)
        self.addAction(self.player)
        self.addAction(self.static)
        self.addAction(self.animated)


class NodeEditor(QtWidgets.QWidget):
    edited = QtCore.Signal()
    fieldEdited = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.node = None
        self.panels = {
            type_: FieldPanel(fields) for type_, fields in FIELDS.items()}

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        for panel in self.panels.values():
            self.layout.addWidget(panel)
            panel.setVisible(False)
            panel.edited.connect(self.edited.emit)
            panel.fieldEdited.connect(self.fieldEdited.emit)

    def set_node(self, node):
        self.node = node
        for panel in self.panels.values():
            panel.hide()
        if node is None:
            return
        panel = self.panels[node.type]
        panel.show()
        panel.values = node.data

    @property
    def values(self):
        if not self.node:
            return {}
        panel = self.panels[self.node.type]
        return panel.values