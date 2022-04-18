import os
import shutil
import traceback
import yaml

import corax.context as cctx


DEFAULTCONFIG = f'{cctx.RESSOURCES_FOLDER}/defaultconfig.yaml'

_cache = None


def load():
    try:
        if not os.path.exists(cctx.CONFIG_FILE):
            shutil.copy(DEFAULTCONFIG, cctx.CONFIG_FILE)
        with open(cctx.CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    except BaseException:
        print(traceback.format_exc())
        with open(DEFAULTCONFIG, 'r') as f:
            global _cache
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
    return _cache.get(key)


def setkey(key, value):
    if not _cache:
        load()
    _cache[key] = value
    save()
