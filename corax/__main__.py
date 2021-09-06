
"""
===============================================================================
|    Welcome to the Corax Engine !                                            |
|                                                                             |
|                                                                             |
|               ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,,,,,,,,,,,,%%%#&%%*,,,,,,,,.,,,                      |
|               ,,,,,,,,,,,,,,,,,#%%%%&@&@&&%&&&&,,,,,,,                      |
|               ,,,,,,,,,,,,,,,,&&&&&##/@%,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,,,,,%%(##&&&&%#%%,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,,,/@/(/(%%&&%##%#,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,.(###&#&##%&&%&%&,,,,,,,,,,,,,,                      |
|               ,,,,,,,,,((%&%&@&&&&%%&%&&,,,,,,,,,,,,,,                      |
|               ,,,,,,,,%@@&&&@&&%&&&&&%%@,,,,,,,,,,,,,,                      |
|               ,,,,,,,/&@&&@&&&&&@@&%&@@,,,,,,,,,,,,,,,                      |
|               ,,,,,,,%&&&@&&&&&&@&&&@&,,,,,,,,,,,,,,,,                      |
|               *****,@&%&@@@@&&@@@@@%,,,,,,,,,,,,,,,,*,                      |
|               ******%%@@@&&&@@@@@#&,,,,,,,,,,,********                      |
|               *****@@@@@@@&&&/#,&,,,,,,,,,,,,,********                      |
|               ****@@@@,. (&%@#,.%#***,,,,,,***********                      |
|                .,*@@@&@@@@****,*(%@.*,,,,*************                      |
|               ,,&@@&@,@@,,,,,,,,,,,%( ,,,,,,,,********                      |
|                                                                             |
|                                                                             |
===============================================================================

To initialize the engine with game data, use in your terminal comand syntax:
python {$CoraxEngineRoot} {$GameDataRoot} [flags]
flags available:
    --help       -h | Show the help. If that flag is set, the engine will not
                    | initialize any game.
    --debug      -d | Run game in debug mode. Add some verbose and render the
                    | infos HUD.
    --mute       -m | Disable all sounds.
    --fullscreen -f | Launch the game in fullscreen mode

===============================================================================

The root folder structure must be sctrict:
---> root
 |---> animations
 |---> moves
 |---> scenes
 |---> scripts
 |---> sets
 |---> sounds
 \---> main.json

Each folder is the sub-root used as relative path by the engine for each
concerned data type. Note that the folder stucture can be inside each sub-roots.

    -- animations --
Contains the game spritesheet as PNG. A sprite sheet is a
collection of frames save as table. The size of each frame is strict. It can be
defined for each sprite sheet but it is constant for the all sprite sheet.
The engine will automatically split animation using the frame data assigned.

    -- moves --
Contains the spritesheet data which is basically: inputs management, event
triggers, move coordinate, frame data, etc. Those files are JSON.

    -- scenes --
Contains all the level data files as json.

    -- players --
Contains all the players data as json.

    -- scripts --
This folder contains all the crackle scripts. Crackle script is the Corax
scripting langage used to script the story, the event and the game
interactions.

    -- sets --
Contains all the static graphics images as PNG.

    -- sounds --
All game sounds, it support OGG and WAV.

    -- main.json --
This file is the summary of the game. It also contains the property as the
resolution, the name of the game and the list of the levels.

"""


import os
import sys
import copy
# exit() function is only built-in in interactive console. We need to import
# it from sys for cx_Freeze's compiled version.
from sys import exit

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


if len(sys.argv) == 1:
    raise ValueError(
        "Corax Engine cannot be launched without arguments."
        "Use --help flag to see more details.")
if "--help" in sys.argv or "-h" in sys.argv:
    print(__doc__)
    exit()
import logging
if "--debug" in sys.argv or "-d" in sys.argv:
    logging.getLogger().setLevel(logging.DEBUG)


import corax.context as cctx
from corax.core import RUN_MODE
from corax.theatre import Theatre
from corax.pygameutils import render_centered_text, escape_in_events

# Initializr the constante based on the passed application argument and loads
# the main.json file.
game_data = cctx.initialize(sys.argv)

# PyGame2 initialize needed modules
import pygame
clock = pygame.time.Clock()
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()
screen_mode_flags = 0
screen_mode_flags |= pygame.SCALED
if "--fullscreen" in sys.argv or "-f" in sys.argv:
    screen_mode_flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode(cctx.RESOLUTION, screen_mode_flags)

# Theatre is the main controller class. It drive the story, build and load the
# scenes.
theatre = Theatre(copy.deepcopy(game_data))
pygame.display.set_caption(theatre.caption)

text = "Connect game controller (X Input)"
while pygame.joystick.get_count() == 0:
    pygame.joystick.quit()
    pygame.joystick.init()
    render_centered_text(screen, text, (255, 255, 255))
    pygame.display.flip()
    clock.tick(cctx.FPS)

joystick = pygame.joystick.Joystick(0)
# game loop
done = False
while not done:
    if theatre.run_mode == RUN_MODE.RESTART:
        theatre.audio_streamer.stop()
        theatre = Theatre(copy.deepcopy(game_data))
    joystick.init()
    events = pygame.event.get()
    done = joystick.get_button(7) == 1 or escape_in_events(events)
    theatre.evaluate(joystick, screen)
    pygame.display.flip()
    clock.tick(cctx.FPS)
