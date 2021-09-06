import json
import os
from PyQt5 import QtWidgets, QtCore
import corax.context as cctx
from pluck.sprite import AnimationDataEditor
from pluck.highlighter import get_plaint_text_editor
from pluck.scene import SceneEditor


SUPPORTED_FILETYPES = "sheets", "scenes", "scripts"


def detect_filetype(filename):
    folder = os.path.dirname(filename)
    while os.path.realpath(os.path.dirname(folder)) != os.path.realpath(cctx.ROOT):
        folder = os.path.dirname(folder)
        if os.path.realpath(cctx.ROOT) not in os.path.realpath(folder):
            return None
        continue
    return os.path.basename(folder)


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


class PluckMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_explorer_model = QtWidgets.QFileSystemModel()
        self.project_explorer = QtWidgets.QTreeView()
        self.project_explorer.setModel(self.project_explorer_model)
        self.project_explorer.doubleClicked.connect(self.request_open_file)

        self.scenes = None
        self.spritesheets = None
        self.scripts = None

        self.area = QtWidgets.QMdiArea()
        self.area.setViewMode(QtWidgets.QMdiArea.TabbedView)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.project_explorer)
        self.splitter.addWidget(self.area)

        self.setCentralWidget(self.splitter)

    def set_workspace(self, workspace):
        # cctx.initialize(workspace)
        root = self.project_explorer_model.setRootPath(workspace)
        self.project_explorer.setRootIndex(root)

    def create_tab_window(self, tabname, widget, name):
        tab_window = QtWidgets.QTabWidget()
        tab_window.setWindowTitle(tabname)
        tab_window.setTabsClosable(True)
        self.area.addSubWindow(tab_window)
        tab_window.addTab(widget, name + "  ")
        tab_window.show()
        return tab_window

    def add_scene(self, name, widget):
        try:
            if not self.scenes:
                raise RuntimeError
            self.scenes.isVisible()
            self.scenes.addTab(widget, name + "  ")

        except RuntimeError:
            self.scenes = self.create_tab_window("scene", widget, name)

    def add_spritesheet(self, name, widget):
        try:
            if not self.spritesheets:
                raise RuntimeError
            self.spritesheets.isVisible()
            self.spritesheets.addTab(widget, name + "  ")

        except RuntimeError:
            self.spritesheets = self.create_tab_window("sheet", widget, name)

    def add_script(self, name, widget):
        try:
            if not self.scripts:
                raise RuntimeError
            self.scripts.isVisible()
            self.scripts.addTab(widget, name + "  ")

        except RuntimeError:
            self.scripts = self.create_tab_window("script", widget, name)

    def request_open_file(self):
        indexes = self.project_explorer.selectionModel().selectedIndexes()
        if not indexes:
            return
        filenames = {self.project_explorer_model.filePath(i) for i in indexes}
        for filename in filenames:
            filetype = detect_filetype(filename)
            if filetype not in SUPPORTED_FILETYPES:
                continue
            elif filetype == "sheets":
                spritesheet = load_json(filename)
                self.add_spritesheet(
                    os.path.basename(filename),
                    AnimationDataEditor(spritesheet))
            elif filetype == "scripts":
                with open(filename, "r") as f:
                    text = f.read()
                script, h = get_plaint_text_editor("crackle")
                script.setPlainText(text)
                self.add_script(os.path.basename(filename), script)
            elif filetype == "scenes":
                scene = SceneEditor(load_json(filename), cctx)
                self.add_scene(os.path.basename(filename), scene)

