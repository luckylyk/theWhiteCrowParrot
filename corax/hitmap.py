
from corax.mathutils import sum_num_arrays


def detect_hitmap_collision(hitmap1, hitmap2, block_position1, block_position2, print_=False):
    for block1 in hitmap1:
        block1 = sum_num_arrays(block1, block_position1)
        for block2 in hitmap2:
            block2 = sum_num_arrays(block2, block_position2)
            if block1 == block2:
                return True
    return False
