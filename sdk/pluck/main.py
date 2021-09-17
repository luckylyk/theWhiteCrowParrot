import json
import os
from functools import partial
from PyQt5 import QtWidgets, QtCore, QtGui
import corax.context as cctx
from pluck.sprite import AnimationDataEditor
from pluck.highlighter import get_plaint_text_editor
from pluck.scene import SceneEditor
from pluck.qtutils import wait_cursor, get_icon, set_shortcut


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
        set_shortcut("CTRL+S", self, self.save_current_tab)

        self.project_explorer_model = QtWidgets.QFileSystemModel()
        self.project_explorer = QtWidgets.QTreeView()
        self.project_explorer.setModel(self.project_explorer_model)
        self.project_explorer.doubleClicked.connect(self.request_open_file)

        self.tab = QtWidgets.QTabWidget()
        self.tab.setTabsClosable(True)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.project_explorer)
        self.splitter.addWidget(self.tab)

        self.setCentralWidget(self.splitter)

    def set_workspace(self, workspace):
        # cctx.initialize(workspace)
        root = self.project_explorer_model.setRootPath(workspace)
        self.project_explorer.setRootIndex(root)

    @wait_cursor
    def add_widget(self, name, widget):
        self.tab.addTab(widget, name)
        method = partial(self.set_savable_tab, widget)
        try:
            widget.modified.connect(method)
        except AttributeError:
            # Widget is not ready to trace change and not able to save files
            pass

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
        indexes = self.project_explorer.selectionModel().selectedIndexes()
        if not indexes:
            return
        filenames = {self.project_explorer_model.filePath(i) for i in indexes}
        for filename in filenames:
            filetype = detect_filetype(filename)
            if filetype not in SUPPORTED_FILETYPES:
                continue
            tabname = os.path.basename(filename)
            if filetype == "sheets":
                spritesheet = load_json(filename)
                widget = AnimationDataEditor(spritesheet)
            elif filetype == "scripts":
                with open(filename, "r") as f:
                    text = f.read()
                widget, _ = get_plaint_text_editor("crackle")
                widget.setPlainText(text)
            else: #filetype == "scenes":
                widget = SceneEditor(load_json(filename), cctx)
            widget.filename = filename
            self.add_widget(tabname, widget)