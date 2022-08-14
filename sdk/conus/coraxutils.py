import glob
import json
import os

from PIL import Image

import corax.context as cctx
from corax.core import NODE_TYPES

from conus.imgutils import remove_key_color


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


def init_corax(path):
    MockArguments.game_root = os.path.abspath(path)
    return cctx.initialize(MockArguments)


def scene_to_display_image(filename):
    with open(f'{cctx.SCENE_FOLDER}/{filename}', 'r') as file:
        data = json.load(file)

    bg = Image.new(
        'RGBA',
        (data['boundary'][2], data['boundary'][3]),
        tuple(data['background_color']))
    for element in data['elements']:
        if element['type'] != NODE_TYPES.SET_STATIC:
            continue
        filepath = f'{cctx.SET_FOLDER}/{element["file"]}'
        image = remove_key_color(filepath)
        bg.paste(image, element['position'], image)
    return bg


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def list_all_scenes():
    filepaths = glob.glob(f'{cctx.SCENE_FOLDER}/**/*.json', recursive=True)
    names = [load_json(f)['name'] for f in filepaths]
    filenames = [f[len(cctx.SCENE_FOLDER):] for f in filepaths]
    return list(zip(names, filenames))
