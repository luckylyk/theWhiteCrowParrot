import os
import json
from functools import partial

import corax.context as cctx
from corax.pygameutils import load_image
from corax.euclide import Rect
from corax.graphicelement import SetStaticElement, SetAnimatedElement
from corax.camera import Camera, Scrolling
from corax.core import NODE_TYPES
from corax.animation import SpriteSheet
from corax.cordinates import Cordinates
from corax.moves import MovementManager
from corax.player import Player
from corax.zone import NoGo
from corax.sounds import (
    Ambiance, SfxSoundCollection, SoundShooter, SfxSound)
from corax.particles import (
    ParticlesSystem, Spot, DirectionBehavior, build_emitter)


class Scene():
    def __init__(
            self,
            name,
            background_color,
            camera=None,
            scrolling=None,
            sound_shooter=None):
        self.name = name
        self.camera = camera
        self.background_color = background_color
        self.scrolling = scrolling
        self.layers = []
        self.players = []
        self.sounds = []
        self.sound_shooter = sound_shooter
        self.evaluables = []
        self.zones = []

    @property
    def elements(self):
        return [e for l in self.layers for e in l.elements]

    def append(self, layer):
        self.layers.append(layer)

    def render(self, screen):
        screen.fill(self.background_color)
        for layer in sorted(self.layers, key=lambda layer: layer.deph):
            for element in layer.elements:
                element.render(screen, layer.deph, self.camera)
        for sound in self.sounds:
            sound.update()
        for zone in self.zones:
            zone.render(screen, self.camera)
        self.sound_shooter.shoot()


class Layer():
    def __init__(self, name, deph, elements):
        self.elements = elements
        self.name = name
        self.deph = deph

    def append(self, element):
        self.elements.append(element)


def check_first_layer(level_datas):
    if level_datas["elements"][0]["type"] != NODE_TYPES.LAYER:
        raise ValueError("first scene element must be a Layer")


def build_set_static_element(datas):
    return SetStaticElement.from_filename(
        os.path.join(cctx.SET_FOLDER, datas["file"]),
        pixel_position=datas["position"],
        key_color=cctx.KEY_COLOR,
        deph=datas["deph"])


def build_set_animated_element(datas):
    return SetAnimatedElement.from_filename(
        os.path.join(cctx.MOVE_FOLDER, datas["file"]),
        pixel_position=datas["position"],
        deph=datas["deph"])


def build_player(datas, grid_pixel_offset, input_buffer, sound_shooter):
    data_path = os.path.join(cctx.MOVE_FOLDER, datas.get("movedatas_file"))
    with open(data_path, "r") as f:
        move_datas = json.load(f)
    spritesheet = SpriteSheet.from_filename(data_path)
    position = datas["block_position"]
    cordinates = Cordinates(
        block_position=position, pixel_offset=grid_pixel_offset)
    movementmanager = MovementManager(move_datas, spritesheet, cordinates)
    name = datas["name"]

    return Player(
        name,
        movementmanager,
        input_buffer,
        cordinates,
        sound_shooter)


def build_scrolling(camera, level_datas):
    hard_boundary = Rect(*level_datas["boundary"])
    soft_boundaries = [Rect(*b) for b in level_datas["soft_boundaries"]]
    return Scrolling(
        camera,
        soft_boundaries=soft_boundaries,
        hard_boundary=hard_boundary,
        target_offset=level_datas["target_offset"])


def build_ambiance(datas):
    return Ambiance(
        filename=datas["file"],
        zone=datas["zone"],
        falloff=datas["falloff"],)


def build_sfx_sound(datas):
    return SfxSound(
        name=datas["name"],
        filename=datas["filename"],
        trigger=datas["trigger"],
        falloff=datas["falloff"],
        zone=datas["zone"])


def build_sfx_collection(datas):
    return SfxSoundCollection(
        name=datas["name"],
        files=datas["files"],
        order=datas["order"],
        trigger=datas["trigger"],
        falloff=datas["falloff"],
        zone=datas["zone"])


def find_element(scene, name):
    for element in scene.elements:
        if element.name == name:
            return element


def build_particles_system(datas):
    zone = Rect(*datas["emission_zone"]) if datas["emission_zone"] else None
    emitter = build_emitter(zone=zone, spots=datas["emission_positions"])
    return ParticlesSystem(
        name=datas["name"],
        zone=datas["zone"],
        alpha=datas["alpha"],
        deph=datas["deph"],
        start_number=datas["start_number"],
        flow=datas["flow"],
        spot_options=datas["spot_options"],
        direction_options=datas["direction_options"],
        shape_options=datas["shape_options"],
        emitter=emitter)


def build_scene(name, level_datas, input_buffer):
    check_first_layer(level_datas)
    camera = Camera()
    scrolling = build_scrolling(camera, level_datas)
    sound_shooter = SoundShooter()
    scene = Scene(
        name=name,
        background_color=level_datas["background_color"],
        camera=camera,
        scrolling=scrolling,
        sound_shooter=sound_shooter)

    for zone_datas in level_datas["zones"]:
        if zone_datas.get("type") == NODE_TYPES.NO_GO:
            zone = NoGo(zone_datas)
            scene.zones.append(zone)

    layer = None
    for element in level_datas["elements"]:
        if element.get("type") == NODE_TYPES.LAYER:
            layer = Layer(element["name"], element["deph"], [])
            scene.layers.append(layer)
            continue
        if element.get("type") == NODE_TYPES.SET_STATIC:
            static = build_set_static_element(element)
            layer.append(static)
        if element.get("type") == NODE_TYPES.SET_ANIMATED:
            animated = build_set_animated_element(element)
            layer.append(animated)
            scene.evaluables.append(animated)
        if element.get("type") == "player":
            offset = level_datas["grid_pixel_offset"]
            player = build_player(element, offset, input_buffer, sound_shooter)
            for zone in scene.zones:
                if player.name in zone.affect:
                    player.add_zone(zone)
            layer.append(player)
            scene.players.append(player)
            scene.evaluables.append(player)
            if player.name == level_datas["scroll_target"]:
                scrolling.target = player.cordinates
        if element.get("type") == NODE_TYPES.PARTICLES:
            particles = build_particles_system(element)
            scene.evaluables.append(particles)
            layer.append(particles)

    ambiances = (NODE_TYPES.AMBIANCE, NODE_TYPES.MUSIC)
    for sound_datas in level_datas["sounds"]:
        if sound_datas.get("type") in ambiances:
            ambiance = build_ambiance(sound_datas)
            element = find_element(scene, sound_datas["listener"])
            ambiance.listener = element.cordinates
            scene.sounds.append(ambiance)
        if sound_datas.get("type") == NODE_TYPES.SFX_COLLECTION:
            collection = build_sfx_collection(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            collection.emitter = element.cordinates
            sound_shooter.sounds.append(collection)
        if sound_datas.get("type") == NODE_TYPES.SFX:
            sound = build_sfx_sound(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            sound.emitter = element.cordinates
            sound_shooter.sounds.append(sound)

    return scene
