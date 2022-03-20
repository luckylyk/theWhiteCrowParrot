import json
import os
import shutil

import corax.context as cctx

from pluck.context import MockArguments
from pluck.data import data_to_plain_text
from pluck.qtutils import HERE


RESSOURCES_PATH = os.path.join(HERE, "ressources")

GAMEFOLDERS = [
    'animations',
    'overrides',
    'players',
    'scripts',
    'scenes',
    'sets',
    'sheets',
    'sounds']
LAYER_FILENAME = os.path.join(RESSOURCES_PATH, "layer.json")
CHARACTER_FILENAME = os.path.join(RESSOURCES_PATH, "character.json")
PLAYER_PLACEHOLDER_FILENAME = os.path.join(RESSOURCES_PATH, "player_placeholder.json")
SCENE_FILENAME = os.path.join(RESSOURCES_PATH, "scene.json")
SCRIPT_FILENAME = os.path.join(RESSOURCES_PATH, "script.ckl")
SET_ANIMATED_FILENAME = os.path.join(RESSOURCES_PATH, "set_animated.json")
SET_STATIC_FILENAME = os.path.join(RESSOURCES_PATH, "set_static.json")
SHEET_FILENAME = os.path.join(RESSOURCES_PATH, "sheet.json")

RESSOURCE_DEFAULT_VALUES = {
    'character': ({'filename': 'character.json', 'name': 'character'}),
    'script': ({'filename': 'script.ckl'}),
    'sheet': ({'filename': 'sheet.json'}),
    'scene': ({'filename': 'scene.json', 'name': 'scene'})
}


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def detect_filetype(filename):
    folder = os.path.dirname(filename)
    while os.path.realpath(os.path.dirname(folder)) != os.path.realpath(cctx.ROOT):
        folder = os.path.dirname(folder)
        if os.path.realpath(cctx.ROOT) not in os.path.realpath(folder):
            return None
        continue
    return os.path.basename(folder)


def ensure_dst_directory_exists(filename):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_character(filename, name):
    print(filename, name, CHARACTER_FILENAME, cctx.CHARACTER_FOLDER)
    return create_file_from_ressources(
        filename, name, CHARACTER_FILENAME, cctx.CHARACTER_FOLDER)


def create_scene(filename, name):
    return create_file_from_ressources(
        filename, name, SCENE_FILENAME, cctx.SCENE_FOLDER)


def create_sheet(filename, name):
    return create_file_from_ressources(
        filename, name, SHEET_FILENAME, cctx.SHEET_FOLDER)


def create_script(filename):
    filename = filename.lower()
    if not filename.endswith(".ckl"):
        filename += ".ckl"
    dst = os.path.join(cctx.SCRIPT_FOLDER, filename)
    ensure_dst_directory_exists(dst)
    if os.path.exists(dst):
        raise FileExistsError(f'{dst} cannot be erased.')
    shutil.copy(SCRIPT_FILENAME, dst)
    return dst


def create_main_file(root, title, scenes, start_scene):
    template_src = os.path.join(RESSOURCES_PATH, 'main.json')
    data = load_json(template_src)
    data['title'] = title
    data['start_scene'] = start_scene
    data['scenes'] = scenes
    dst = os.path.join(root, 'main.json')
    with open(dst, 'w') as f:
        json.dump(data, f)


def create_file_from_ressources(filename, name, template_src, folder_dst):
    data = load_json(template_src)
    data["name"] = name
    filename = filename.lower()
    if not filename.endswith(".json"):
        filename += ".json"
    dst = os.path.join(folder_dst, filename)
    ensure_dst_directory_exists(dst)
    if os.path.exists(dst):
        raise FileExistsError(f'{dst} cannot be erased.')
    with open(dst, "w") as f:
        data = data_to_plain_text(data)
        f.write(data)
    return dst


def create_project(root, title):
    if not os.path.exists(root):
        os.makedirs(root)
    for folder in GAMEFOLDERS:
        dst = os.path.join(root, folder)
        os.mkdir(dst)
    print(root)
    scene_filename = os.path.join(root, 'scenes', 'scene_01.json')
    scenes = [{scene_filename: 'Scene 01'}]
    create_main_file(root, title, scenes, 'Scene 01')
    MockArguments.game_root = root
    cctx.initialize(MockArguments)
    create_scene('scene_01.json' , 'Scene 01')