import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import pygame
pygame.display.set_mode([100, 100])


import corax.context as cctx
cctx.BLOCK_SIZE = 10
# gamedata = cctx.initialize(["", os.path.join(os.path.dirname(__file__), "../..", "whitecrowparrot")])

from corax.coordinate import Coordinate

coordinate1 = Coordinate(flip=False, block_position=[35, 10])
coordinate2 = Coordinate(flip=False, block_position=[45, 10])

print (coordinate1.block_center_distance(coordinate2))
coordinate1.center_offset = 10, 10
print (coordinate1.block_center_distance(coordinate2))
coordinate1.flip = True
print (coordinate1.block_center_distance(coordinate2))