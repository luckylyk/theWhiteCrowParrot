
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
    use_config = False
    use_keyboard = False
