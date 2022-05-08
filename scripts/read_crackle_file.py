import sys
import os

HERE = os.path.dirname(__file__)

sys.path.append(os.path.realpath(os.path.join(HERE, "..")))

import corax.context as cctx

class MockArguments:
    """
    The Corax Engine uses an argparse object to initialize. This is a argparse
    mocker to be able to initialize the engine for sdk uses.
    """
    game_root = ''
    debug = False
    mute = True
    speedup = False
    overrides = None
    use_default_config = True


GAMEDATA_FOLDER = os.path.join(HERE, "../whitecrowparrot")
MockArguments.game_root = os.path.abspath(GAMEDATA_FOLDER)
GAME_DATA = cctx.initialize(MockArguments)

from corax.crackle.io import parse_crackle_file

filepath = os.path.join(cctx.SCRIPT_FOLDER)
scripts, events = parse_crackle_file(os.path.join(filepath, "sinoc.ckl"), "sinoc")
for script in scripts:
    print (script, events)
