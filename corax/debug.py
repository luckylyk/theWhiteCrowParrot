import logging


_debug_mode = False


def get_debug_mode():
    return _debug_mode


def set_debug_mode(state):
    global _debug_mode
    _debug_mode = state
    logging.getLogger().setLevel(logging.DEBUG if state else logging.INFO)


def toggle_debug_mode():
    global _debug_mode
    _debug_mode = not _debug_mode
