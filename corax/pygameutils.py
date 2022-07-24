
"""
This module is the bridge to PyGame. It is supposed to be one the rare import
of it. It wrap the pygame functions to make them as much generic as possible
to make a futur engine change easy. It's mainly helper to get and load pygame
object from files.
"""


import itertools
import os
import pygame

from pygame.locals import QUIT

import corax.context as cctx
from corax.core import COLORS
import corax.screen as sctx


# In order to make the corax as less agnostic as possible from Pygame.
# Each pygame object is stored in this module.  The game itself only store id
# to find binary object saved here.
_image_store = {}
_sound_store = {}


def escape_in_events(events):
    return any(
        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or
        event.type == QUIT
        for event in events)


def load_frames(filename, frame_size, key_color, relative=True):
    """
    Split a huge sheet in memory.
    """
    if relative:
        filename = os.path.join(cctx.ANIMATION_FOLDER, filename)
    sheet = pygame.image.load(filename).convert()
    width, height = frame_size
    row = sheet.get_height() / height
    col = sheet.get_width() / width
    if row != int(row) or col != int(col):
        message = (
            f"the sprite sheet file {filename} size doesn't "
            "match with his block size")
        raise ValueError(message)
    ids = []

    for j, i in itertools.product(range(int(row)), range(int(col))):
        image = pygame.Surface([width, height]).convert()
        x, y = i * width, j * height
        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(key_color)
        id_ = f'{filename}[{i}.{j}]'
        _image_store[id_] = image
        ids.append(id_)
    return ids


def load_image(filename, key_color=None):
    if _image_store.get(filename):
        return filename
    image = pygame.image.load(filename).convert()
    if key_color is not None:
        image.set_colorkey(key_color)
    _image_store[filename] = image
    return filename


def image_mirror(id_, horizontal=True, vertical=False):
    if not _image_store.get(id_):
        raise ValueError(f'Unknown image id {id_}. Cannot generate a mirror.')
    flip_id = f'{id_}['
    if horizontal:
        flip_id += 'h'
    if vertical:
        flip_id += 'v'
    flip_id += ']'
    if not _image_store.get(flip_id):
        image = _image_store[id_]
        mirror = pygame.transform.flip(image, horizontal, vertical)
        _image_store[flip_id] = mirror
    return flip_id


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


def render_image(id_, screen, position, alpha=255):
    image = _image_store[id_]
    if alpha == 255:
        screen.blit(image, position)
        return
    # work around to blit with transparency found on here:
    # https://nerdparadise.com/programming/pygameblitopacity
    # thanks dude !
    x, y = position
    w, h = image.get_size()
    temp = pygame.Surface((w, h)).convert()
    temp.blit(screen, (-x, -y))
    temp.blit(image, (0, 0))
    temp.set_alpha(alpha)
    screen.blit(temp, position)


def render_rect(screen, color, x, y, width, height, alpha=255):
    temp = pygame.Surface((width, height)).convert()
    pygame.draw.rect(temp, color, [0, 0, width, height])
    temp.set_alpha(alpha)
    screen.blit(temp, (x, y))


def render_background(screen, color=None, alpha=255):
    color = color or COLORS.BLACK
    render_rect(
        screen=screen,
        color=color,
        x=0,
        y=0,
        width=sctx.SCREEN[0],
        height=sctx.SCREEN[1],
        alpha=alpha)


def render_ellipse(screen, color, x, y, height, width):
    pygame.draw.ellipse(screen, color, [x, y, height, width])


def render_grid(screen, camera, color, alpha=255):
    temp = pygame.Surface(cctx.RESOLUTION).convert()
    # Render grid
    l = -camera.pixel_position[0] % cctx.BLOCK_SIZE
    while l < cctx.RESOLUTION[0]:
        pygame.draw.line(temp, color, (l, 0), (l, sctx.SCREEN[1]))
        l += cctx.BLOCK_SIZE
    t = sctx.HIGH_LETTERBOX[-1] if sctx.USE_LETTERBOX else 0
    while t < cctx.RESOLUTION[1]:
        pygame.draw.line(temp, color, (0, t), (sctx.SCREEN[0], t))
        t += cctx.BLOCK_SIZE
    temp.set_alpha(alpha)
    screen.blit(temp, (0, 0))


def render_text(screen, color, x, y, text, size=15, bold=False):
    font = pygame.font.SysFont('Consolas', size)
    font.bold = bold
    textsurface = font.render(text, False, color)
    screen.blit(textsurface, (x, y))


def render_centered_text(screen, text, color=None):
    color = color or COLORS.WHITE
    font = pygame.font.SysFont('Consolas', 15)
    text = font.render(text, True, color)
    x, y = sctx.SCREEN
    text_rect = text.get_rect(center=(x / 2, y / 2))
    screen.blit(text, text_rect)


def draw_letterbox(screen):
    if not sctx.USE_LETTERBOX:
        return
    render_rect(screen, COLORS.BLACK, *sctx.HIGH_LETTERBOX)
    render_rect(screen, COLORS.BLACK, *sctx.LOW_LETTERBOX)
