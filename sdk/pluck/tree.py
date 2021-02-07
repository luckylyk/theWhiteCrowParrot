from pluck.datas import extract_scene_properties, data_to_plain_text
from pluck.qtutils import get_icon, ICON_MATCH, get_image
from pluck.paint import get_renderer

from corax.core import NODE_TYPES


class CNode():
    def __init__(self, icon, name=None, data=None, parent=None):
        self._name = name
        self.icon = icon
        self._parent = parent
        self.children = []
        self._data = data
        self.renderer = get_renderer(data)
        self.visible = True
        if parent is not None:
            self._parent.children.append(self)

    @property
    def has_to_be_rendered(self):
        if self.visible is False:
            return False
        return all(p.visible for p in self.parents())

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

    def parents(self):
        parent = self.parent()
        if parent is None:
            return []
        parents = [self.parent()]
        while parent.parent() is not None:
            parent = parent.parent()
            parents.append(parent)
        return parents

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

    zones = CNode(name="zones", icon=get_icon("zone.png"), parent=root)
    for zone in scene_datas["zones"]:
        icon = get_icon(ICON_MATCH[zone["type"]])
        CNode(icon=icon, data=zone, parent=zones)

    icon = get_icon("renderable.png")
    renderable = CNode(icon, name="renderable", parent=root)

    layer = None
    for element in scene_datas["elements"]:
        icon = get_icon(ICON_MATCH[element["type"]])
        if element["type"] == NODE_TYPES.LAYER:
            layer = CNode(icon, data=element, parent=renderable)
            continue
        CNode(icon, data=element, parent=layer)

    return invisible_root


def get_scene(tree):
    return tree.children[0]


def list_sounds(tree):
    return get_scene(tree).children[0].children


def list_layers(tree):
    return get_scene(tree).children[-1].children


def list_zones(tree):
    return get_scene(tree).children[1].children


def tree_to_plaintext(tree, indent=4):
    scene_node = tree.children[0]
    sounds = list_sounds(tree)
    zones = list_zones(tree)
    layers = list_layers(tree)

    plaintext = data_to_plain_text(scene_node.data, indent=0).rstrip("\n }")
    plaintext += ',\n    "sounds": [\n        '
    if sounds:
        for sound in sounds:
            plaintext += data_to_plain_text(sound.data, indent=2) + ",\n        "
        plaintext = plaintext[:-10]
    plaintext += '\n    ],\n    "zones": [\n        '
    if zones:
        for zone in zones:
            plaintext += data_to_plain_text(zone.data, indent=2) + ",\n        "
        plaintext = plaintext[:-10]
    plaintext += '\n    ],\n    "elements": [\n        '
    for layer in layers:
        plaintext += data_to_plain_text(layer.data, indent=2) + ',\n        '
        for graphic in layer.children:
            plaintext += data_to_plain_text(graphic.data, indent=2) + ',\n        '
    plaintext = plaintext[:-10]
    plaintext += "\n    ]\n}"
    return plaintext
