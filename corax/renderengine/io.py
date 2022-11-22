import os
import logging
import itertools

import moderngl
import moderngl_window
import pygame
import corax.context as cctx
from corax.renderengine import shaders


# In order to make the corax as less agnostic as possible from Pygame.
# Each pygame object is stored in this module.  The game itself only store id
# to find binary object saved here.
_image_store = {}
_shader_store = {}
_animation_store = {}


NULL_SHADER = {
    "path": None,
    "use_time": False,
    "use_resolution": False,
    "options": {}
}


def load_shader_program(path=None):
    if path is None:
        fragment_shader = shaders.FRAGMENT_SHADER
    else:
        path = f'{cctx.SHADER_FOLDER}/{path}'
        with open(path, 'r') as f:
            fragment_shader = f.read()
    try:
        program = moderngl_window.ctx().program(
            vertex_shader=shaders.VERTEX_SHADER,
            fragment_shader=fragment_shader)
        return program
    except moderngl.error.Error as e:
        logging.error("Shading Program build fail for:", path)
        raise moderngl.error.Error from e


def get_shader(shader, time, resolution, window_size):
    path = shader['path'] if shader else None
    if not shader:
        return load_shader_program()
    if path not in _shader_store:
        _shader_store[path] = load_shader_program(path)
    program = _shader_store[path]
    if shader['use_time']:
        program['time'] = time
    if shader['use_resolution']:
        program['resolution'] = resolution
        program['window_size'] = window_size
    if shader['options']:
        for key, value in shader['options'].items():
            program[key] = value
    return program


def get_image(id_):
    return _image_store[id_]


def load_frames(filename, frame_size, key_color, relative=True):
    """
    Split a huge sheet in memory.
    """
    if relative:
        filename = os.path.join(cctx.ANIMATION_FOLDER, filename)

    if _animation_store.get(filename):
        return _animation_store.get(filename)

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
    _animation_store[filename] = ids
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
