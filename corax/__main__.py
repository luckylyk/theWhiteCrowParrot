
"""
===============================================================================
|                                                                             |
|   Welcome to the Corax Engine !     `:+ys/                                  |
|                                  -shho:yM+                                  |
|                               `/hho.   oM+                                  |
|                              .y+.      oM+ o/                               |
|                             .h.        oM+`MNy`                             |
|                            .dy  o      oM+`MMMo                             |
|                           :MM-  m      NM/  `                               |
|                           `hN-  -   +yoys-                                  |
|       .+hhhsoooooo:---``````yh`     ho`  `d+------------------              |
|     `-+yhhhhhhhyoo++++//+yd.`ym-    h.   :N--++++++++++syyyyy+`             |
|                          `m+ `hm`   h.   sN -s+/-`                          |
|          .:/oooooooo///-  :h  .No+/+s    hd` .-/+oo//-`                     |
|          ```........``.``./h-  /.``..   `mhys+-.`  ``.`                     |
|                   +o+/++mh   .-+h/ .ho-  .+y//osyy+.                        |
|                      `yo` `dh:hMNNmmNNoss+. -y`                             |
|                      +s   .MNmMNh:`./NMNMM+  s.                             |
|                     -ms   `/sNMh    :dmo++`  :o                             |
|                     oms    .+NMNy+ohNmMNh.   /o                             |
|                     -dN`   +NMmyyMMMm:s+/`  .m.                             |
|                       oNd-       ::-.    .od:                               |
|                        :yms:.         ./oy+`                                |
|                       :: .`/oss/////+:o/.-`                                 |
|               ```  -h/                    oy                                |
|           `:+o+/:  ..                      o.                               |
|           -..  .o/                          `                               |
|               :h+`--                         . .-.`                         |
|              /-   `y                       y-// .:++:`                      |
|                   `d                       o` o:                            |
|                   `:                       /   +.                           |
===============================================================================
"""

import os
import sys
# exit() function is only built-in in interactive console. We need to import
# it from sys for cx_Freeze's compiled version.
from sys import exit

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


if len(sys.argv) == 1:
    raise ValueError(
        "Corax Engine cannot be launched without arguments."
        "Use --help flag to see more details.")


print(__doc__)
if "--help" in sys.argv or "-h" in sys.argv:
    from corax.help import HELP
    print(HELP)
    exit()


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("game_root", type=str)
parser.add_argument("-d", "--debug", action='store_true')
parser.add_argument("-f", "--fullscreen", action='store_true')
parser.add_argument("-m", "--mute", action='store_true')
parser.add_argument("-o", "--overrides", type=str)
parser.add_argument("-s", "--scaled", action='store_true')
parser.add_argument("-ss", "--skip_splash", action='store_true')
parser.add_argument("-sp", "--speedup", action='store_true')
arguments = parser.parse_args()


if arguments.debug:
    import logging
    logging.getLogger().setLevel(logging.DEBUG)


import corax.context as cctx
from corax.gameloop import GameLoop
from corax.screen import setup_display
from corax import config
# Initialize the engine constants based on the application arguments and loads
# the main.json file.
game_data = cctx.initialize(arguments)

# PyGame2 initialize needed modules
import pygame
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()
screen = setup_display(
    scaled=arguments.scaled or config.get('scaled'),
    fullscreen=arguments.fullscreen or config.get('fullscreen'))


# This execute the Corax Engine splash screen.
if not arguments.skip_splash:
    from corax.splash import splash_screen, SPLASH_FPS
    splash = splash_screen(screen)
    clock = pygame.time.Clock()
    for _ in splash:
        pygame.display.flip()
        clock.tick(SPLASH_FPS)


# Run the game
gameloop = GameLoop(game_data, screen)
while not gameloop.done:
    next(gameloop)
