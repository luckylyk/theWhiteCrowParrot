from PyQt5 import QtCore
from corax.core import ELEMENT_TYPES
from corax.cordinates import Cordinates
from scene_editor.datas import SET_TYPES


def grow_rect(rect, value):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() - value,
        rect.top() - value,
        rect.width() + (value * 2),
        rect.height() + (value * 2))


def get_element_cordinate(element, grid_offset=None):
    if element["type"] in SET_TYPES:
        return Cordinates(
            mirror=False,
            block_position=(0, 0),
            pixel_offset=element["position"])
    if element["type"] == ELEMENT_TYPES.PLAYER:
        return Cordinates(
            mirror=False,
            block_position=element["block_position"],
            pixel_offset=grid_offset)
