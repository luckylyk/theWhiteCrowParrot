import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pygame
from corax.data import get_animation_data
from corax.iterators import frame_data_iterator
from corax.animation import AnimationSheet

pygame.init()

animdata = get_animation_data("whitecrowparrot_sword.json")
frame_data = animdata["animations"]["step_forward"]["frames"]
print(frame_data)
iterator = frame_data_iterator(frame_data)

for stuff in iterator:
    print(stuff)


animationsheet = AnimationSheet(animdata)