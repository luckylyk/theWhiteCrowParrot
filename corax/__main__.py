
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
    --debug      -d | Run game in debug mode. Add some verbose and render the
                    | infos HUD.
    --fullscreen -f | Launch the game in fullscreen mode.
    --help       -h | Show the help. If that flag is set, the engine will not
                    | initialize any game.
    --mute       -m | Disable all sounds.
    --scaled -s     | Scaled pixels

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


if "--debug" in sys.argv or "-d" in sys.argv:
    import logging
    logging.getLogger().setLevel(logging.DEBUG)


import corax.context as cctx
from corax.gameloop import GameLoop
from corax.pygameutils import setup_display
# Initializr the constante based on the passed application argument and loads
# the main.json file.
game_data = cctx.initialize(sys.argv)
# PyGame2 initialize needed modules
import pygame
pygame.joystick.init()
pygame.mixer.init()
pygame.font.init()

screen = setup_display(game_data["title"], sys.argv)
gameloop = GameLoop(game_data, screen)
while not gameloop.done:
    next(gameloop)

