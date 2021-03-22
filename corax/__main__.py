
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

To initialize the engine with game data, use in your terminal command that
argument list:
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
triggers, move coordinates, frame data, etc. Those files are JSON.

    -- scenes --
Contains all the level data files as json.

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

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
except NameError:
    # This means the script is running under py2exe distribution.
    # Add the corax path to the system becomes useless in order that
    # py2exe is automatically adding the current folder to the distribution.
    # By the way, we have to import exit from sys as far as it is in the global
    # scope of an py2exe executable.
    from sys import exit


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
from corax.theatre import Theatre

# Initializr the constante based on the passed application argument and loads
# the main.json file.
game_datas = cctx.initialize(sys.argv)

# PyGame2 initialize needed modules
import pygame
clock = pygame.time.Clock()
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()
screen_mode_flags = 0
if "--fullscreen" in sys.argv or "-f" in sys.argv:
    screen_mode_flags |= pygame.SCALED
    screen_mode_flags |= pygame.FULLSCREEN
screen = pygame.display.set_mode(cctx.RESOLUTION, screen_mode_flags)

# Theatre is the main controller class. It drive the story, build and load the
# scenes.
theatre = Theatre(game_datas)
pygame.display.set_caption(theatre.caption)
joystick = pygame.joystick.Joystick(0)

# game loop
done = False
while not done:
    joystick.init()
    done = joystick.get_button(7) == 1
    pygame.event.get()
    theatre.evaluate(joystick, screen)
    clock.tick(cctx.FPS)
    pygame.display.flip()
