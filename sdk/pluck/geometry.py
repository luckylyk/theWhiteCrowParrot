from PySide6 import QtCore
from corax.core import NODE_TYPES
import corax.context as cctx
from pluck.data import SET_TYPES
from pluck.qtutils import get_image


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
    if element["type"] == NODE_TYPES.PLAYER:
        x, y = element["block_position"]
        x *= cctx.BLOCK_SIZE
        y *= cctx.BLOCK_SIZE
        return x, y


def pixel_position(block_position):
    x = block_position[0] * cctx.BLOCK_SIZE
    y = block_position[1] * cctx.BLOCK_SIZE
    return x, y


def status_bar_rects(rect, paintcontext):
    main_rect = QtCore.QRect(
        0, rect.height() - paintcontext.status_bar_height,
        rect.width(), paintcontext.status_bar_height)
    padding = paintcontext.status_bar_text_padding
    pixel_coord_rect = QtCore.QRect(
        padding,
        rect.height() - paintcontext.status_bar_height + padding,
        paintcontext.status_bar_pos_width,
        paintcontext.status_bar_height - (2 * padding))
    block_coord_rect = QtCore.QRect(
        padding * 3 + paintcontext.status_bar_pos_width,
        rect.height() - paintcontext.status_bar_height + padding,
        paintcontext.status_bar_pos_width,
        paintcontext.status_bar_height - (2 * padding))
    highlighted_rect = QtCore.QRect(
        (padding * 5) + (paintcontext.status_bar_pos_width * 2),
        rect.height() - paintcontext.status_bar_height + padding,
        rect.width() - paintcontext.status_bar_pos_width - (4 * padding),
        paintcontext.status_bar_height - (2 * padding))
    return {
        'bar': main_rect,
        'pixel_coord': pixel_coord_rect,
        'block_coord': block_coord_rect,
        'highlighted': highlighted_rect}


def status_thumbnail_rect(rect, image, paintcontext):
    original_width = image.width()
    original_height = image.height()
    if original_width < original_height:
        height = paintcontext.thumbnail_max_size
        factor = original_height / height
        width = original_width // factor
    else:
        width = paintcontext.thumbnail_max_size
        factor = original_width / width
        height = original_height // factor
    left = rect.right() - width
    top = rect.bottom() - height - paintcontext.status_bar_height
    return QtCore.QRect(left, top, width, height)


def get_node_rect(node, paintcontext):
    data = node.data
    if zone := data.get('zone'):
        rect = QtCore.QRect()
        rect.setTopLeft(QtCore.QPoint(zone[0], zone[1]))
        rect.setBottomRight(QtCore.QPoint(zone[2], zone[3]))
        rect = paintcontext.relatives_rect(rect)
        return rect
    elif (img := get_image(data)):
        if (pos := data.get('position')):
            x, y = pos
        elif (pos := data.get('block_position')):
            x, y = pos[0] * cctx.BLOCK_SIZE, pos[1] * cctx.BLOCK_SIZE
        else:
            return
        rect = QtCore.QRect()
        rect.setTopLeft(QtCore.QPoint(x, y))
        rect.setWidth(img.width())
        rect.setHeight(img.height())
        rect = paintcontext.relatives_rect(rect)
        return rect
