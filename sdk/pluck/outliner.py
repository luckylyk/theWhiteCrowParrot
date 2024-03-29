from PySide6 import QtWidgets, QtCore


class OutlinerView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)


class OutlinerTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(OutlinerTreeModel, self).__init__(parent)
        self._root = root

    def set_tree(self, tree):
        self.layoutAboutToBeChanged.emit()
        self._root = tree
        self.layoutChanged.emit()

    def rowCount(self, parent):
        if not parent.isValid():
            return self._root.childCount()
        return parent.internalPointer().childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.name
        if role == QtCore.Qt.DecorationRole:
            return node.icon
        if role == QtCore.Qt.CheckStateRole:
            return QtCore.Qt.Checked if node.visible else QtCore.Qt.Unchecked

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and section == 0:
            return "Scene"

    def flags(self, index):
        return (
            QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsUserCheckable)

    def setData(self, index, value, role):
        node = self.getNode(index)
        if role == QtCore.Qt.CheckStateRole:
            node.visible = bool(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def parent(self, index):
        node = self.getNode(index)
        parent = node.parent()
        if parent == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def index(self, row, column, parent=QtCore.QModelIndex()):
        parent = self.getNode(parent)
        child = parent.child(row)
        if not child:
            return QtCore.QModelIndex()
        return self.createIndex(row, column, child)

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root
