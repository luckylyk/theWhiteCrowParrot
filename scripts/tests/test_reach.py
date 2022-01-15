import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.display.set_mode([100, 100])


import corax.context as cctx

gamedata = cctx.initialize(["", os.path.join(os.path.dirname(__file__), "..", "whitecrowparrot")])


from corax.player import load_players
from corax.sequence import build_sequence_to_destination

player = load_players()[0]
player.set_sheet("exploration")
player.coordinate.block_position = [15, 10]
moves = "return", "run_a", "walk_a", "footsie"
data = player.animation_controller.data
coordinate = player.coordinate
print(build_sequence_to_destination(moves, data, coordinate, [15, 10]))
sequence = build_sequence_to_destination(moves, data, coordinate, [53, 10])
print(sum(sum(data["moves"][move]["frames_per_image"]) for move in sequence))
print(build_sequence_to_destination(moves, data, coordinate, [53, 10]))
print(build_sequence_to_destination(moves, data, coordinate, [1, 10]))
print(build_sequence_to_destination(moves, data, coordinate, [51, 10]))
print(build_sequence_to_destination(moves, data, coordinate, [42, 10]))
