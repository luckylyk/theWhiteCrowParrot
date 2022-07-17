import os
import shutil
import traceback
import yaml

import corax.context as cctx


DEFAULTCONFIG = f'{cctx.RESSOURCES_FOLDER}/defaultconfig.yaml'

_cache = None


def load():
    global _cache
    try:
        if not os.path.exists(cctx.CONFIG_FILE):
            directory = os.path.dirname(cctx.CONFIG_FILE)
            if not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copy(cctx.DEFAULT_CONFIG_FILE, cctx.CONFIG_FILE)
        with open(cctx.CONFIG_FILE, 'r') as f:
            _cache = yaml.safe_load(f)
            return _cache
    except BaseException:
        print(traceback.format_exc())
        with open(DEFAULTCONFIG, 'r') as f:
            _cache = yaml.safe_load(f)
            return _cache


def save():
    if not _cache:
        raise RuntimeError('Config not loaded.')
    with open(cctx.CONFIG_FILE, 'r') as f:
        yaml.safe_dump(_cache, f)


def get(key):
    if not _cache:
        load()
        print('cache', _cache)
    print('loaded', _cache)
    return _cache.get(key)


def setkey(key, value):
    if not _cache:
        load()
    _cache[key] = value
    save()
