from PyQt5 import QtCore
from corax.core import ELEMENT_TYPES
from corax.cordinates import Cordinates
import corax.context as cctx
from scene_editor.datas import SET_TYPES


def grow_rect(rect, value):
    if not rect:
        return None
    return QtCore.QRectF(
        rect.left() - value,
        rect.top() - value,
        rect.width() + (value * 2),
        rect.height() + (value * 2))


def get_position(element, grid_offset=None):
    if element["type"] in SET_TYPES:
        return element["position"]
    if element["type"] == ELEMENT_TYPES.PLAYER:
        x, y = element["block_position"]
        x *= cctx.BLOCK_SIZE
        y *= cctx.BLOCK_SIZE
        return x, y