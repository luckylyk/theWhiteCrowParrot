
from functools import partial
import os
from re import A
import subprocess
import sys

from PySide6 import QtWidgets, QtCore, QtGui

import corax.context as cctx

from pluck.data import data_to_plain_text
from pluck.dialog import GameKicker, CreateRessourceFileDialog
from pluck.highlighter import get_plaint_text_editor
from pluck.jsonmodel import QJsonModel
from pluck.project import ProjectManager
from pluck.qtutils import wait_cursor, get_icon, set_shortcut
from pluck.ressource import (
    RESSOURCE_DEFAULT_VALUES, detect_filetype, load_json, create_character,
    create_scene, create_sheet, create_script)
from pluck.sanity import data_sanity_check
from pluck.scene import SceneEditor
from pluck.sheet import SheetEditor


SUPPORTED_FILETYPES = "sheets", "scenes", "scripts"
WINDOW_TITLE = "Pluck"


class PluckMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        set_shortcut("CTRL+S", self, self.save_current_tab)
        set_shortcut("CTRL+P", self, self.kick_game)

        self.project_explorer_toolbar = ProjectToolbar()
        self.project_explorer_toolbar.runRequested.connect(self.kick_game)
        self.project_explorer_toolbar.createItemRequested.connect(self.create_item)

        self.project_explorer_model = QtWidgets.QFileSystemModel()
        self.project_explorer_tree = QtWidgets.QTreeView()
        self.project_explorer_tree.setModel(self.project_explorer_model)
        for i in range(1, self.project_explorer_model.columnCount()):
            self.project_explorer_tree.hideColumn(i)
        self.project_explorer_tree.doubleClicked.connect(self.request_open_file)

        self.project_explorer = QtWidgets.QWidget()
        self.project_explorer_layout = QtWidgets.QVBoxLayout(self.project_explorer)
        self.project_explorer_layout.setContentsMargins(0, 0, 0, 0)
        self.project_explorer_layout.addWidget(self.project_explorer_toolbar)
        self.project_explorer_layout.addWidget(self.project_explorer_tree)

        self.project_manager = ProjectManager()
        self.project_manager.edited.connect(self.edit_game_settings)
        data = load_json(cctx.GAME_FILE)
        self.project_manager.settings = data
        self.project_manager.preferences = data["preferences"]

        self.project_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.project_splitter.sizeHint = lambda: QtCore.QSize(250, 400)
        self.project_splitter.addWidget(self.project_explorer)
        self.project_splitter.addWidget(self.project_manager)

        self.tab = QtWidgets.QTabWidget()
        self.tab.sizeHint = lambda: QtCore.QSize(800, 800)
        self.tab.setTabsClosable(True)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.project_splitter)
        self.splitter.addWidget(self.tab)

        self.setCentralWidget(self.splitter)
        self.sizeHint = lambda: QtCore.QSize(1200, 800)

    def set_workspace(self, workspace):
        self.setWindowTitle(WINDOW_TITLE + " - " + cctx.TITLE)
        root = self.project_explorer_model.setRootPath(workspace)
        self.project_explorer_tree.setRootIndex(root)

    @wait_cursor
    def add_widget(self, name, widget):
        self.tab.addTab(widget, name)
        self.tab.setCurrentWidget(widget)
        method = partial(self.set_savable_tab, widget)
        try:
            widget.modified.connect(method)
        except AttributeError:
            # Widget is not ready to trace change and not able to save files
            pass

    def create_item(self, type_):
        kwargs = RESSOURCE_DEFAULT_VALUES[type_]
        dialog = CreateRessourceFileDialog(**kwargs)
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return
        try:
            match type_:
                case 'character':
                    create_character(filename=dialog.filename, name=dialog.name)
                case 'sheet':
                    create_sheet(filename=dialog.filename, name=dialog.name)
                case 'script':
                    create_script(filename=dialog.filename)
                case 'scene':
                    create_scene(filename=dialog.filename, name=dialog.name)
        except FileExistsError as e:
            QtWidgets.QMessageBox.critical(
                self, 'Create file error',
                f'{dialog.filename} already exists. Cannot be erase.')

    def kick_game(self):
        dialog = GameKicker()
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return
        corax_root = os.path.join(os.path.dirname(__file__), "../../corax")
        arguments = [
            sys.executable, corax_root, cctx.ROOT, *dialog.arguments(),
            '--use_default_config']
        subprocess.Popen(arguments)

    def set_savable_tab(self, widget):
        for i in range(self.tab.count()):
            if widget == self.tab.widget(i):
                break
        else: # widget doesn't exist
            return
        self.tab.setTabIcon(i, get_icon("save.png"))

    def save_current_tab(self):
        widget = self.tab.currentWidget()
        if not widget.is_modified:
            return
        widget.save(widget.filename)
        index = self.tab.currentIndex()
        self.tab.setTabIcon(index, QtGui.QIcon())

    def request_open_file(self):
        indexes = self.project_explorer_tree.selectionModel().selectedIndexes()
        if not indexes:
            return
        filenames = {self.project_explorer_model.filePath(i) for i in indexes}
        for filename in filenames:
            if os.path.isdir(filename):
                continue
            filetype = detect_filetype(filename)
            tabname = os.path.basename(filename)
            if filetype == "sheets":
                spritesheet = load_json(filename)
                widget = SheetEditor(spritesheet)
            elif filetype == "scripts":
                with open(filename, "r") as f:
                    text = f.read()
                widget, _ = get_plaint_text_editor("crackle")
                widget.setPlainText(text)
            elif filetype == "scenes":
                widget = SceneEditor(load_json(filename), cctx)
            elif filename.endswith(".json"):
                model = QJsonModel()
                widget = QtWidgets.QTreeView()
                widget.setModel(model)
                model.load(load_json(filename))
            else:
                continue
            widget.filename = filename
            self.add_widget(tabname, widget)

    def edit_game_settings(self):
        try:
            data_sanity_check(self.project_manager.preferences, "game_preferences")
            data_sanity_check(self.project_manager.settings, "game_settings")
            self.project_manager.clean_error()
        except Exception as e:
            self.project_manager.set_error(str(e))
            return
        data = load_json(cctx.GAME_FILE)
        data.update(self.project_manager.settings)
        data["preferences"].update(self.project_manager.preferences)
        with open(cctx.GAME_FILE, "w") as f:
            f.write(data_to_plain_text(data))


class ProjectToolbar(QtWidgets.QToolBar):
    runRequested = QtCore.Signal()
    createItemRequested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QtCore.QSize(12, 12))
        self.run = QtGui.QAction(get_icon("play.png"), "", self)
        self.run.triggered.connect(self.runRequested.emit)

        self.create_item = QtGui.QAction(get_icon("plus.png"), "", self)
        self.create_item.triggered.connect(self._call_create_item)

        self.create_actions = []
        for item in RESSOURCE_DEFAULT_VALUES:
            action = QtGui.QAction(item.capitalize())
            method = partial(self.createItemRequested.emit, item)
            action.triggered.connect(method)
            self.create_actions.append(action)

        self.addAction(self.run)
        self.addAction(self.create_item)

    def _call_create_item(self):
        menu = QtWidgets.QMenu(self)
        for action in self.create_actions:
            menu.addAction(action)

        menu.exec(QtGui.QCursor.pos())