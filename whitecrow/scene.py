import os
import json
from functools import partial

from whitecrow.loaders import load_image
from whitecrow.euclide import Rect
from whitecrow.graphicelement import StaticElement
from whitecrow.camera import Camera, Scrolling, get_render_zone
from whitecrow.core import ELEMENT_TYPES, COLORS, SOUND_TYPES
from whitecrow.constants import SET_FOLDER, MOVE_FOLDER
from whitecrow.animation import SpriteSheet
from whitecrow.cordinates import Cordinates
from whitecrow.moves import MovementManager
from whitecrow.player import Player
from whitecrow.sounds import (
    Ambiance, SfxSoundCollection, SoundShooter, SfxSound)
from whitecrow.particles import (
    ParticlesSystem, Spot, DirectionBehavior, build_emitter)


class Scene():
    def __init__(self, camera=None, scrolling=None, sound_shooter=None):
        self.camera = camera
        self.scrolling = scrolling
        self.layers = []
        self.players = []
        self.sounds = []
        self.sound_shooter = sound_shooter
        self.particles = []
        self.render_zone = get_render_zone()

    @property
    def elements(self):
        return [e for l in self.layers for e in l.elements]

    def append(self, layer):
        self.layers.append(layer)

    def render(self, screen):
        for layer in sorted(self.layers, key=lambda layer: layer.elevation):
            for element in layer.elements:
                world_pos = element.pixel_position
                elev = layer.elevation + element.elevation
                cam_pos = self.camera.relative_pixel_position(world_pos, elev)
                element.render(screen, cam_pos)
        for sound in self.sounds:
            sound.update()
        self.sound_shooter.shoot()


class Layer():
    def __init__(self, name, elevation, elements):
        self.elements = elements
        self.name = name
        self.elevation = elevation

    def append(self, element):
        self.elements.append(element)


def check_first_layer(level_datas):
    if level_datas["elements"][0]["type"] != ELEMENT_TYPES.LAYER:
        raise ValueError("first scene element must be a Layer")


def build_static_element(datas):
    return StaticElement.from_filename(
        os.path.join(SET_FOLDER, datas["file"]),
        pixel_position=datas["position"],
        key_color=COLORS.GREEN,
        elevation=datas["elevation"])


def build_player(datas, grid_pixel_offset, input_buffer, sound_shooter):
    data_path = os.path.join(MOVE_FOLDER, datas.get("movedatas_file"))
    with open(data_path, "r") as f:
        move_datas = json.load(f)
    spritesheet = SpriteSheet.from_filename(data_path)
    position = datas["block_position"]
    cordinates = Cordinates(position=position, pixel_offset=grid_pixel_offset)
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
        elevation=datas["elevation"],
        start_number=datas["start_number"],
        flow=datas["flow"],
        spot_options=datas["spot_options"],
        direction_options=datas["direction_options"],
        shape_options=datas["shape_options"],
        emitter=emitter)


def build_scene(level_datas, input_buffer):
    check_first_layer(level_datas)

    camera = Camera()
    scrolling = build_scrolling(camera, level_datas)
    sound_shooter = SoundShooter()
    scene = Scene(
        camera=camera,
        scrolling=scrolling,
        sound_shooter=sound_shooter)

    layer = None
    for element in level_datas["elements"]:
        if element.get("type") == ELEMENT_TYPES.LAYER:
            layer = Layer(element["name"], element["elevation"], [])
            scene.layers.append(layer)
            continue
        if element.get("type") == ELEMENT_TYPES.STATIC:
            static = build_static_element(element)
            layer.append(static)
        if element.get("type") == "player":
            offset = level_datas["grid_pixel_offset"]
            player = build_player(element, offset, input_buffer, sound_shooter)
            layer.append(player)
            scene.players.append(player)
            if player.name == level_datas["scroll_target"]:
                scrolling.target = player.cordinates
        if element.get("type") == ELEMENT_TYPES.PARTICLES:
            particles = build_particles_system(element)
            scene.particles.append(particles)
            layer.append(particles)

    for sound_datas in level_datas["sounds"]:
        if sound_datas.get("type") == SOUND_TYPES.AMBIANCE:
            ambiance = build_ambiance(sound_datas)
            element = find_element(scene, sound_datas["listener"])
            ambiance.listener = element.cordinates
            scene.sounds.append(ambiance)
        if sound_datas.get("type") == SOUND_TYPES.SFX_COLLECTION:
            collection = build_sfx_collection(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            collection.emitter = element.cordinates
            sound_shooter.sounds.append(collection)
        if sound_datas.get("type") == SOUND_TYPES.SFX:
            sound = build_sfx_sound(sound_datas)
            element = find_element(scene, sound_datas["emitter"])
            sound.emitter = element.cordinates
            sound_shooter.sounds.append(sound)

    return scene
