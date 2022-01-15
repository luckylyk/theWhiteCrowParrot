
HELP = """
To initialize the engine with game data, use in your terminal comand syntax:
python {$CoraxEngineRoot} {$GameDataRoot} [flags]
flags available:

    --debug        -d | Run game in debug mode. Add some verbose and render the
                      | infos HUD.
    --fullscreen   -f | Launch the game in fullscreen mode.
    --help         -h | Show the help. If that flag is set, the engine will not
                      | initialize any game.
    --mute         -m | Disable all sounds.
    --overrides    -o | Path to an override json file. For debug purpose, this
                      | is usefull for to change the start spot of the game
                      | without editing the game data.
    --scaled -s       | Scaled pixels
    --skip_splash -ss | Skip Corax Splash screen. This is for debug purpose.
                      | This is not mandatory, but keeping the splash screen
                      | enable with distributed version of software would be
                      | appreciated.
    --speedup     -sp | Run the game twice faster

===============================================================================

The root folder structure must be sctrict:
---> root
 |---> animations
 |---> characters
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

    -- characters --
Contains the characters configuration files. Basically a character is a
spritesheet assembly.

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
