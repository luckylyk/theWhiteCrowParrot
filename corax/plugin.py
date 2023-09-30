
import sys

import corax.context as cctx


plugins = {}


def register_custom_plugins():
    sys.path.append(cctx.ROOT)
    from plugins import PLUGIN_SHAPES
    for cls in PLUGIN_SHAPES:
        if cls.ptype in plugins:
            raise ValueError(
                'Plugin registration Error: '
                'Name clash: another plugin '
                f'already registered with name {cls.name}')
        plugins[cls.ptype] = cls


def build_plugin_shape(data, scene):
    ptype = data['ptype']
    cls = plugins.get(ptype)
    if cls is None:
        raise ValueError(f'Unkown plugin-type: {ptype}')
    return cls(data['name'], scene, data)


def list_registered_plugin_shape_classes():
    return list(plugins.values())
