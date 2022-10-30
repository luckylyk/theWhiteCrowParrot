import os
import pygame
import corax.context as cctx

# In order to make the corax as less agnostic as possible from Pygame.
# Each pygame object is stored in this module. The game itself only store id
# to find binary object saved here.
_sound_store = {}


def load_sound(filename):
    filename = os.path.join(cctx.SOUNDS_FOLDER, filename)
    if _sound_store.get(filename):
        return filename
    try:
        _sound_store[filename] = pygame.mixer.Sound(filename)
        return filename
    except FileNotFoundError as e:
        msg = f"No such file or directory: {filename}"
        raise FileNotFoundError(msg) from e


def play_sound(id_, loop=False):
    sound = _sound_store.get(id_)
    if not sound:
        raise ValueError(f'Sound "{id_}" is not loaded')
    if loop:
        _sound_store[id_].play(-1)
        return
    _sound_store[id_].play()


def stop_sound(id_):
    sound = _sound_store.get(id_)
    if not sound:
        raise ValueError(f'Sound "{id_}" is not loaded')
    return _sound_store[id_].stop()


def get_volume(id_):
    sound = _sound_store.get(id_)
    if not sound:
        raise ValueError(f'Sound "{id_}" is not loaded')
    return _sound_store[id_].get_volume()


def set_volume(id_, volume):
    sound = _sound_store.get(id_)
    if not sound:
        raise ValueError(f'Sound "{id_}" is not loaded')
    return _sound_store[id_].set_volume(volume)
