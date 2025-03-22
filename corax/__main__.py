"""
===============================================================================
|                                                                             |
|   Welcome to the Corax Engine !     ░▒█▒▒▒                                  |
|                                  ▀▒▓▓▒░▒█▄                                  |
|                               ░▒▓▓▒░   ▒█▄                                  |
|                              ░▒▄░      ▒█▄ ▒▒                               |
|                             ░▓░        ▒█▄░█▓▒░                             |
|                            ░▓▒  ▒      ▒█▄░███▒                             |
|                           ░██▀  █      ▓█▒  ░                               |
|                           ░▓▓▀  ▀   ▄▒▒▒▒▀                                  |
|       ░▄▓▓▓▒▒▒▒▒▒▒░▀▀▀░░░░░░▒▓░     ▓▒░  ░▓▄▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀              |
|     ░▀▄▒▓▓▓▓▓▓▓▒▒▒▄▄▄▄▒▒▄▒▓░░▒█▀    ▓░   ░▓▀▀▄▄▒▒▒▒▒▒▒▒▒▒▒▒▄░               |
|            ░░░░░░░░░░░░░░░█▄ ░▓█░   ▓░   ▒▓ ▀▒▄▒▀░                          |
|          ░░▒▒ ▒▒▒▒ ▒▒▒▒▀  ░▓  ░▓▒▄▒▄▒    ▓▓░ ░▀▒▄▒▒▒▒▀░                     |
|               ░░ ░░ ░░░░░▒▓▀  ▒░░░░░   ░█▓▒▒▄▀░░  ░░░░                      |
|                   ▄▒▄▒▄▄█▓   ░▀▄▓▒ ░▓▒▀  ░▄▒▒▒▒▒▒▒▄░                        |
|                      ░▒▒░ ░▓▓░▓█▓▓██▓▓▒▒▒▄░ ▀▒░                             |
|                      ▄▒   ░█▓██▓▓░░░▒▓█▓██▄  ▒░                             |
|                     ▀█▒   ░▒▒▓█▓    ░▓█▒▄▄░  ░▒                             |
|                     ▒█▒    ░▄▓█▓▒▄▒▓▓██▓▓░   ▒▒                             |
|                     ▀▓▓░   ▄▓██▒▒████░▒▄▒░  ░█░                             |
|                       ▒▓▓▀       ░░▀░    ░▒▓░                               |
|                        ░▒█▒░░         ░▒▒▒▄░                                |
|                       ░░ ░░▒▒▒▒▒▒▒▒▒▄░▒▒░▀░                                 |
|               ░░░  ▀▓▒                    ▒▒                                |
|           ░░▄▒▄▒░  ░░                      ▒░                               |
|           ▀░░  ░▒▒                          ░                               |
|               ░▓▄░▀▀                         ░ ░▀░░                         |
|              ▒▀   ░▒                       ▒▀▒▒ ░░▄▄░░                      |
|                   ░▓                       ▒░ ▒░                            |
|                   ░░                       ▒   ▄░                           |
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
parser.add_argument("-udc", "--use_default_config", action='store_true')
parser.add_argument("-uc", "--use_config", action='store_true')
parser.add_argument("-o", "--overrides", type=str)
parser.add_argument("-s", "--scaled", action='store_true')
parser.add_argument("-ss", "--skip_splash", action='store_true')
parser.add_argument("-sp", "--speedup", action='store_true')
parser.add_argument("-k", "--use_keyboard", action='store_true')
arguments = parser.parse_args()


import corax.context as cctx
from corax import renderengine, config
from corax.debug import set_debug_mode
from corax.gameloop import GameLoop
from corax.gamepad import load_config_keybinding
from corax.plugin import register_custom_plugins
from corax.screen import initialize_screen
from corax.renderengine.display import setup_render_display
from corax.renderengine.draw import render, render_splash

set_debug_mode(arguments.debug)

# Initialize the engine constants based on the application arguments and loads
# the main.json file.
game_data = cctx.initialize(arguments)
load_config_keybinding()

# PyGame2 initialize needed modules
import pygame
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()

sc = config.get('scaled') if cctx.USE_CONFIG else arguments.scaled
fs = config.get('fullscreen') if cctx.USE_CONFIG else arguments.fullscreen

window = setup_render_display(scaled=sc, fullscreen=fs)
initialize_screen(cctx.RESOLUTION)
renderengine.initialize()

# This execute the Corax Engine splash screen.
if not arguments.skip_splash:
    from corax.splash import splash_screen, SPLASH_FPS
    clock = pygame.time.Clock()
    splash = splash_screen()
    for background_color, alpha, images_kwargs in splash:
        events = pygame.event.get()
        render_splash(window, background_color, alpha, images_kwargs, events)
        clock.tick(SPLASH_FPS)

# Run the game
register_custom_plugins()
gameloop = GameLoop(game_data)

while not gameloop.done:
    events = pygame.event.get()
    gameloop.__next__(events)
    render(gameloop, window, events)
