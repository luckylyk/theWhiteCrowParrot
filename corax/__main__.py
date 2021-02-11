
"""
==========================================================================================
|    Welcome to the Corax Engine !                                                       |
==========================================================================================

To initialize the engine with game data, use in your terminal command that argument list:
python "corax engine folder" "game data root folder" [flags]
flags available:
   --help       -h | Show the help. If that flag is set, the engine will not initialize any game.
   --debug      -d | Run game in debug mode. Add some verbose and render the infos HUD.
   --mute       -m | Disable all sounds.
   --fullscreen -f | Launch the game in fullscreen mode
"""

import os
import json
import sys
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

if not sys.argv:
    raise ValueError("No arguments passed to launch the script")

if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    exit()

if "--debug" in sys.argv or "-d" in sys.argv:
    logging.getLogger().setLevel(logging.DEBUG)


import pygame
import corax.context as cctx
from corax.theatre import Theatre

game_datas = cctx.initialize(sys.argv)
clock = pygame.time.Clock()
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()

screen_mode_flags = pygame.SCALED
if "--fullscreen" in sys.argv or "-f" in sys.argv:
    screen_mode_flags |= pygame.FULLSCREEN

screen = pygame.display.set_mode(cctx.RESOLUTION, screen_mode_flags)

theatre = Theatre(game_datas)
pygame.display.set_caption(theatre.caption)
joystick = pygame.joystick.Joystick(0)

done = False


while not done:
    joystick.init()

    done = joystick.get_button(7) == 1
    pygame.event.get()
    theatre.evaluate(joystick, screen)
    clock.tick(cctx.FPS)
    pygame.display.flip()
