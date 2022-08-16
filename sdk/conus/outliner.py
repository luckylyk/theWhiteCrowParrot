import json
from PySide6 import QtWidgets
from corax.core import NODE_TYPES
import corax.context as cctx
from conus.qtutils import get_icon


SUPPORTED_NODES = NODE_TYPES.SET_STATIC, NODE_TYPES.LAYER


class TreeWidget(QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.levels = QtWidgets.QPushButton(get_icon('histogram.png'), '')
        self.hsv = QtWidgets.QPushButton(get_icon('exposition.png'), '')
        self.label = QtWidgets.QLabel(name)
        self.label.setFixedWidth(150)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)
        self.layout.addWidget(self.levels)
        self.layout.addWidget(self.hsv)


def build_scene_tree(filename, tree):
    with open(f'{cctx.SCENE_FOLDER}/{filename}', 'r') as f:
        data = json.load(f)
    root = QtWidgets.QTreeWidgetItem()
    root.setText(0, data['name'])
    layers = []
    for element in data['elements']:
        if element.get('type') not in SUPPORTED_NODES:
            continue

        widget = TreeWidget(element.get('name'))
        if element.get('type') == NODE_TYPES.LAYER:
            layer = QtWidgets.QTreeWidgetItem(root)
            layers.append(layer)
            tree.setItemWidget(layer, 0, widget)

        elif element.get('type') == NODE_TYPES.SET_STATIC:
            item = QtWidgets.QTreeWidgetItem(layers[-1])
            tree.setItemWidget(item, 0, widget)

    return [root]
