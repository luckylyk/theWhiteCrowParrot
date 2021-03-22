from PyQt5 import QtWidgets, QtCore
import corax.context as cctx


class PluckMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_explorer_model = QtWidgets.QFileSystemModel()
        self.project_explorer = QtWidgets.QTreeView()
        self.project_explorer.setModel(self.project_explorer_model)

        self.scenes = QtWidgets.QTabWidget()
        self.spritsheets = QtWidgets.QTabWidget()
        self.scripts = QtWidgets.QTabWidget()

        self.area = QtWidgets.QMdiArea()
        self.area.addSubWindow(self.scenes)
        self.area.addSubWindow(self.spritsheets)
        self.area.addSubWindow(self.scripts)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.project_explorer)
        self.splitter.addWidget(self.area)

        self.setCentralWidget(self.splitter)

    def set_workspace(self, workspace):
        # cctx.initialize(workspace)
        root = self.project_explorer_model.setRootPath(workspace)
        self.project_explorer.setRootIndex(root)

    def add_scene(self, name, widget):
        self.scenes.addTab(widget, name)

    def add_spritesheet(self, name, widget):
        self.spritsheets.addTab(widget, name)

    def add_script(self, name, widget):
        self.scripts.addTab(widget, name)
