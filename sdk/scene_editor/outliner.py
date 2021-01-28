from PyQt5 import QtWidgets, QtCore


class OutlinerView(QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)


class OutlinerTreeModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(OutlinerTreeModel, self).__init__(parent)
        self._root = root

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

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and section == 0:
            return "Scene"

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def parent(self, index):
        node = self.getNode(index)
        parent = node.parent()
        if parent == self._root:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row(), 0, parent)

    def index(self, row, column, parent):
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

    # def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
    #     parent_node = self.getNode(parent)
    #     self.beginInsertRows(parent, position, position + rows - 1)

    #     for _ in range(rows):
    #         childCount = parent_node.childCount()
    #         childNode = Node("untitled" + str(childCount))
    #         success = parent_node.insertChild(position, childNode)

    #     self.endInsertRows()
    #     return success

    # def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
    #     parent_node = self.getNode(parent)
    #     self.beginRemoveRows(parent, position, position + rows - 1)
    #     for _ in range(rows):
    #         success = parent_node.removeChild(position)
    #     self.endRemoveRows()
    #     return success