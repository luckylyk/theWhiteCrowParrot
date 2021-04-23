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
from corax.coordinates import Coordinate
from corax.moves import AnimationController
from corax.player import Player
from corax.zone import Zone
from corax.sounds import (
    Ambiance, SfxSoundCollection, SoundShooter, SfxSound)
from corax.particles import (
    ParticlesSystem, Spot, DirectionBehavior, build_emitter)
from corax.debugrender import render_player_debug


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
        self.animated_sets = []
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
        if cctx.DEBUG:
            for player in self.players:
                render_player_debug(player, layer.deph, screen, self.camera)


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


def build_set_static_element(data):
    return SetStaticElement.from_filename(
        os.path.join(cctx.SET_FOLDER, data["file"]),
        pixel_position=data["position"],
        key_color=cctx.KEY_COLOR,
        deph=data["deph"])


def build_set_animated_element(data):
    return SetAnimatedElement.from_filename(
        data["name"],
        os.path.join(cctx.MOVE_FOLDER, data["file"]),
        pixel_position=data["position"],
        deph=data["deph"],
        alpha=data["alpha"])


def build_player(data, grid_pixel_offset, input_buffer, sound_shooter):
    filename = data.get("movedatas_file")
    data_path = os.path.join(cctx.MOVE_FOLDER, filename)
    with open(data_path, "r") as f:
        move_datas = json.load(f)
    spritesheet = SpriteSheet.from_filename(filename, data_path)
    position = data["block_position"]
    coordinates = Coordinate(
        block_position=position, pixel_offset=grid_pixel_offset)
    animation_controller = AnimationController(move_datas, spritesheet, coordinates)
    name = data["name"]
    return Player(
        name,
        animation_controller,
        input_buffer,
        coordinates,
        sound_shooter)


def build_scrolling(camera, level_datas):
    hard_boundary = Rect(*level_datas["boundary"])
    soft_boundaries = [Rect(*b) for b in level_datas["soft_boundaries"]]
    return Scrolling(
        camera,
        soft_boundaries=soft_boundaries,
        hard_boundary=hard_boundary,
        target_offset=level_datas["target_offset"])


def build_ambiance(data):
    return Ambiance(
        filename=data["file"],
        zone=data["zone"],
        falloff=data["falloff"],)


def build_sfx_sound(data):
    return SfxSound(
        name=data["name"],
        filename=data["filename"],
        trigger=data["trigger"],
        falloff=data["falloff"],
        zone=data["zone"])


def build_sfx_collection(data):
    return SfxSoundCollection(
        name=data["name"],
        files=data["files"],
        order=data["order"],
        trigger=data["trigger"],
        falloff=data["falloff"],
        zone=data["zone"])


def find_element(scene, name):
    for element in scene.elements:
        if element.name == name:
            return element


def find_animated_set(scene, name):
    for element in scene.animated_sets:
        if element.name == name:
            return element


def find_player(scene, name):
    for player in scene.players:
        if player.name == name:
            return player


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
        if zone_datas.get("type") in (NODE_TYPES.NO_GO, NODE_TYPES.INTERACTION):
            zone = Zone(zone_datas)
            scene.zones.append(zone)

    layer = None
    for element in level_datas["elements"]:
        if element.get("type") == NODE_TYPES.LAYER:
            layer = Layer(element["name"], element["deph"], [])
            scene.layers.append(layer)
            continue
        elif element.get("type") == NODE_TYPES.SET_STATIC:
            static = build_set_static_element(element)
            layer.append(static)
        elif element.get("type") == NODE_TYPES.SET_ANIMATED:
            animated = build_set_animated_element(element)
            layer.append(animated)
            scene.evaluables.append(animated)
            scene.animated_sets.append(animated)
        elif element.get("type") == "player":
            offset = level_datas["grid_pixel_offset"]
            player = build_player(element, offset, input_buffer, sound_shooter)
            for zone in scene.zones:
                if player.name in zone.affect:
                    player.add_zone(zone)
            layer.append(player)
            scene.players.append(player)
            scene.evaluables.append(player)
            if player.name == level_datas["scroll_target"]:
                scrolling.target = player.coordinates
        elif element.get("type") == NODE_TYPES.PARTICLES:
            particles = build_particles_system(element)
            scene.evaluables.append(particles)
            layer.append(particles)

    ambiances = (NODE_TYPES.AMBIANCE, NODE_TYPES.MUSIC)
    for sound_datas in level_datas["sounds"]:
        if sound_datas.get("type") in ambiances:
            ambiance = build_ambiance(sound_datas)
            element = find_element(scene, sound_datas["listener"])
            ambiance.listener = element.coordinates
            scene.sounds.append(ambiance)
        elif sound_datas.get("type") == NODE_TYPES.SFX_COLLECTION:
            collection = build_sfx_collection(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            collection.emitter = element.coordinates
            sound_shooter.sounds.append(collection)
        elif sound_datas.get("type") == NODE_TYPES.SFX:
            sound = build_sfx_sound(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            sound.emitter = element.coordinates
            sound_shooter.sounds.append(sound)

    return scene
