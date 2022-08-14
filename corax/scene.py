import os

import corax.context as cctx
from corax.camera import Camera, Scrolling
from corax.core import NODE_TYPES
from corax.debugrender import render_player_debug
from corax.euclide import Rect
from corax.graphicelement import SetStaticElement, SetAnimatedElement
from corax.particles import ParticlesSystem, build_emitter
from corax.character import CharacterSlot
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

    def render(self, screen):
        screen.fill(self.background_color)
        for layer in sorted(self.layers, key=lambda layer: layer.deph):
            for element in layer.elements:
                if not element.visible:
                    continue
                element.render(screen, layer.deph, self.camera)
        for zone in self.zones:
            zone.render(screen, self.camera)
        if cctx.DEBUG:
            for slot in self.player_slots + self.npc_slots:
                if slot.character is None:
                    continue
                render_player_debug(
                    player=slot.character,
                    deph=layer.deph,
                    screen=screen,
                    camera=self.camera)


class Layer():
    def __init__(self, name, deph, elements):
        self.elements = elements
        self.name = name
        self.deph = deph

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


def build_scene(name, data):
    assert_first_is_layer(data)
    camera = Camera()
    scrolling = build_scrolling(camera, data)
    scene = Scene(
        name=name,
        background_color=data["background_color"],
        camera=camera,
        scrolling=scrolling)
    build_scene_zones(scene, data)
    build_scene_layers(scene, data)
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


def build_scene_layers(scene, data):
    layer = None
    for element in data["elements"]:
        if element.get("type") == NODE_TYPES.LAYER:
            layer = Layer(element["name"], element["deph"], [])
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

        elif element.get("type") == NODE_TYPES.NPC:
            slot = build_character_slot(element)
            layer.append(slot)
            scene.npc_slots.append(slot)
            scene.evaluables.append(slot)

        elif element.get("type") == NODE_TYPES.PARTICLES:
            particles = build_particles_system(element)
            scene.evaluables.append(particles)
            layer.append(particles)
