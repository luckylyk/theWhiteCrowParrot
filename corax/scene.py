import os
from copy import deepcopy

import corax.context as cctx
from corax.camera import Camera, Scrolling
from corax.character import CharacterSlot
from corax.core import NODE_TYPES
from corax.euclide import Rect
from corax.graphicelement import SetStaticElement, SetAnimatedElement
from corax.particles import ParticlesSystem, build_emitter
from corax.specialeffect import SpecialEffectsEmitter
from corax.zone import Zone


class Scene:
    def __init__(
            self,
            name,
            background_color,
            camera=None,
            scrolling=None):
        self.name = name
        self.camera = camera
        self.background_color = background_color
        self.scrolling = scrolling
        self.player_slots = []
        self.npc_slots = []
        self.special_effects = []
        self.layers = []
        self.animated_sets = []
        self.evaluables = []
        self.zones = []

    @property
    def elements(self):
        return [e for l in self.layers for e in l.elements]

    def evaluate(self):
        for element in self.evaluables:
            element.evaluate()

    def append(self, layer):
        self.layers.append(layer)


class Layer():
    def __init__(self, name, deph, shader):
        self.elements = []
        self.name = name
        self.deph = deph
        self.shader = shader

    def append(self, element):
        self.elements.append(element)

    def remove(self, element):
        self.elements.remove(element)

    def insert(self, index, element):
        self.elements.insert(index, element)


def assert_first_is_layer(data):
    if data["elements"][0]["type"] != NODE_TYPES.LAYER:
        raise ValueError("first scene element must be a Layer")


def layover(layers, element, target):
    """
    function to put a layer above another one at rendering time.
    """
    for layer in layers:
        if element in layer.elements:
            layer.remove(element)
    for layer in layers:
        if target in layer.elements:
            index = layer.elements.index(target)
            layer.elements.insert(index + 1, element)
            return
    msg = f'Layover error: {element.name} or {target.name} not found.'
    raise ValueError(msg)


def build_set_static_element(data):
    return SetStaticElement.from_filename(
        name=data["name"],
        filename=os.path.join(cctx.SET_FOLDER, data["file"]),
        pixel_position=data["position"],
        key_color=cctx.KEY_COLOR,
        visible=data['visible'],
        deph=data["deph"])


def build_character_slot(data):
    return CharacterSlot(
        name=data["name"],
        block_position=data["block_position"],
        flip=data["flip"])


def build_set_animated_element(data):
    return SetAnimatedElement.from_filename(
        data["name"],
        os.path.join(cctx.SHEET_FOLDER, data["file"]),
        pixel_position=data["position"],
        deph=data["deph"],
        visible=data["visible"],
        alpha=data["alpha"])


def build_scrolling(camera, data):
    hard_boundary = Rect(*data["boundary"])
    soft_boundaries = [Rect(*b) for b in data["soft_boundaries"]]
    return Scrolling(
        camera,
        soft_boundaries=soft_boundaries,
        hard_boundary=hard_boundary,
        target_offset=data["target_offset"])


def build_particles_system(data):
    zone = Rect(*data["emission_zone"]) if data["emission_zone"] else None
    emitter = build_emitter(zone=zone, spots=data["emission_positions"])
    return ParticlesSystem(
        name=data["name"],
        zone=data["zone"],
        alpha=data["alpha"],
        deph=data["deph"],
        start_number=data["start_number"],
        flow=data["flow"],
        spot_options=data["spot_options"],
        direction_options=data["direction_options"],
        shape_options=data["shape_options"],
        emitter=emitter)


def build_special_effect_emitter(data):
    filename = f'{cctx.SHEET_FOLDER}/{data["spritesheet_filename"]}'
    return SpecialEffectsEmitter(
        name=data["name"],
        spritesheet_filename=filename,
        layers=data["layers"],
        alpha=data["alpha"],
        animation_iteration_type=data["animation_iteration_type"],
        deph=data["deph"],
        repeat_delay=data["repeat_delay"],
        persistents=data["persistents"])


def build_scene(name, data, shaders):
    assert_first_is_layer(data)
    camera = Camera()
    scrolling = build_scrolling(camera, data)
    scene = Scene(
        name=name,
        background_color=data["background_color"],
        camera=camera,
        scrolling=scrolling)
    build_scene_zones(scene, data)
    build_scene_layers(scene, data, shaders)
    return scene


def build_scene_zones(scene, data):
    for zone_data in data["zones"]:
        types = (
            NODE_TYPES.NO_GO,
            NODE_TYPES.INTERACTION,
            NODE_TYPES.RELATIONSHIP,
            NODE_TYPES.COLLIDER,
            NODE_TYPES.EVENT_ZONE)
        if zone_data.get("type") in types:
            zone = Zone(zone_data)
            scene.zones.append(zone)


def build_shader(data, shaders):
    if not data:
        return None
    shader = deepcopy(shaders[data["name"]])
    shader["options"].update(data["options"])
    return shader


def build_scene_layers(scene, data, shaders):
    layer = None
    for element in data["elements"]:
        if element.get("type") == NODE_TYPES.LAYER:
            shader = build_shader(element['shader'], shaders)
            layer = Layer(element["name"], element["deph"], shader)
            scene.layers.append(layer)
            continue

        if not layer:
            continue

        if element.get("type") == NODE_TYPES.SET_STATIC:
            static = build_set_static_element(element)
            layer.append(static)

        elif element.get("type") == NODE_TYPES.SET_ANIMATED:
            animated = build_set_animated_element(element)
            layer.append(animated)
            scene.evaluables.append(animated)
            scene.animated_sets.append(animated)

        elif element.get("type") == NODE_TYPES.PLAYER:
            slot = build_character_slot(element)
            layer.append(slot)
            scene.player_slots.append(slot)
            scene.evaluables.append(slot)

        elif element.get("type") == NODE_TYPES.SPECIAL_EFFECTS_EMITTER:
            emitter = build_special_effect_emitter(element)
            layer.append(emitter)
            scene.special_effects.append(emitter)
            scene.evaluables.append(emitter)

        elif element.get("type") == NODE_TYPES.NPC:
            slot = build_character_slot(element)
            layer.append(slot)
            scene.npc_slots.append(slot)
            scene.evaluables.append(slot)

        elif element.get("type") == NODE_TYPES.PARTICLES:
            particles = build_particles_system(element)
            scene.evaluables.append(particles)
            layer.append(particles)
