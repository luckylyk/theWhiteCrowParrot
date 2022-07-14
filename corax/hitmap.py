import corax.context as cctx
from corax.euclide import Rect
from corax.mathutils import sum_num_arrays


def detect_hitmaps_collision(
        hitmap1, hitmap2, block_position1=None, block_position2=None):
    """
    Detect that two given hitmaps are overlapping.
    A hitmap contains absolute coordinates, then for each hitmap, you can
    provide a block position to offset (e.g character position).
    """
    block_position1 = block_position1 or (0, 0)
    block_position2 = block_position2 or (0, 0)
    for block1 in hitmap1:
        block1 = sum_num_arrays(block1, block_position1)
        for block2 in hitmap2:
            block2 = sum_num_arrays(block2, block_position2)
            if block1 == block2:
                return True
    return False


def hitmap_collide_zone(hitmap, zone, block_position=None):
    block_position = block_position or (0, 0)
    rect1 = Rect(zone.l, zone.t, zone.r, zone.b)
    for block in hitmap:
        block = sum_num_arrays(block, block_position)
        rect2 = Rect.xywh(block[0], block[1], 1, 1)
        if rect1.collide_rect(rect2):
            return True
    return False
