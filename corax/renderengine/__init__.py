from corax.renderengine.io import preload_characters


def initialize(no_preload=False):
    if no_preload:
        return
    preload_characters()
