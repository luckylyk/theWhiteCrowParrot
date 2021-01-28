from scene_editor.datas import extract_scene_properties
from scene_editor.qtutils import get_icon, ICON_MATCH, get_image
from scene_editor.paint import get_renderer

from corax.core import ELEMENT_TYPES


class CNode():
    def __init__(self, icon, name=None, data=None, parent=None):
        self._name = name
        self.icon = icon
        self._parent = parent
        self.children = []
        self._data = data
        self.renderer = get_renderer(data)
        if parent is not None:
            self._parent.children.append(self)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self.renderer = get_renderer(data)

    @property
    def type(self):
        if self.data is not None:
            return self.data["type"]

    @property
    def name(self):
        if self._name is not None:
            return self._name

        if self.data is not None:
            return self.data.get("name", "unnamed")

    def childCount(self):
        return len(self.children)

    def parent(self):
        return self._parent

    def child(self, row):
        return self.children[row]

    def row(self):
        if self._parent is not None:
            return self._parent.children.index(self)

    def flat(self):
        childs = self.children[:]
        for child in self.children:
            childs.extend(child.flat())
        return childs

    def render(self, painter, paintcontext):
        if self.renderer is None:
            return
        self.renderer(painter=painter, paintcontext=paintcontext)


def create_scene_outliner_tree(scene_datas):
    invisible_root = CNode(None)
    datas = extract_scene_properties(scene_datas)
    root = CNode(None, data=datas, parent=invisible_root)
    sounds = CNode(get_icon("sound.png"), name="audios", parent=root)

    for sound in scene_datas["sounds"]:
        icon = get_icon(ICON_MATCH[sound["type"]])
        CNode(icon=icon, data=sound, parent=sounds)

    CNode(name="zones", icon=get_icon("zone.png"), parent=root)

    icon = get_icon("renderable.png")
    renderable = CNode(icon, name="renderable", parent=root)

    layer = None
    for element in scene_datas["elements"]:
        icon = get_icon(ICON_MATCH[element["type"]])
        if element["type"] == ELEMENT_TYPES.LAYER:
            layer = CNode(icon, data=element, parent=renderable)
            continue
        CNode(icon, data=element, parent=layer)

    return invisible_root


def list_sounds(tree):
    return tree.children[0].children[0].children


def list_layers(tree):
    return tree.children[0].children[-1].children

