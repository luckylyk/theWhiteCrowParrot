import os
import json

from whitecrow.graphicutils import load_image
from whitecrow.euclide import Rect
from whitecrow.graphicelement import StaticElement
from whitecrow.camera import Camera, Scrolling
from whitecrow.core import ELEMENT_TYPE, COLORS
from whitecrow.constants import SET_FOLDER, MOVE_FOLDER
from whitecrow.animation import SpriteSheet
from whitecrow.cordinates import Cordinates
from whitecrow.moves import MovementManager
from whitecrow.player import Player


class Scene():
    def __init__(self, camera=None, scrolling=None):
        self.camera = camera
        self.scrolling = scrolling
        self.layers = []
        self.players = []

    def append(self, layer):
        self.layers.append(layer)

    def render(self, screen):
        for layer in sorted(self.layers, key=lambda layer: layer.elevation):
            for element in layer.elements:
                world_pos = element.pixel_position
                elev = layer.elevation + element.elevation
                cam_pos = self.camera.relative_pixel_position(world_pos, elev)
                screen.blit(element.image, cam_pos)
                if isinstance(element, Player):
                    print (element.image, element.name)


class Layer():
    def __init__(self, name, elevation, elements):
        self.elements = elements
        self.name = name
        self.elevation = elevation

    def append(self, element):
        self.elements.append(element)


def check_first_layer(level_datas):
    if level_datas["elements"][0]["type"] != ELEMENT_TYPE.LAYER:
        raise ValueError("first scene element must be a Layer")


def build_static_element(datas):
    return StaticElement.from_filepath(
        os.path.join(SET_FOLDER, datas["file"]),
        pixel_position=datas["position"],
        key_color=COLORS.GREEN,
        elevation=datas["elevation"])


def build_player(datas, grid_pixel_offset, input_buffer):
    data_path = os.path.join(MOVE_FOLDER, datas.get("movedatas_file"))
    with open(data_path, "r") as f:
        move_datas = json.load(f)
    spritesheet = SpriteSheet.from_datafile(data_path)
    position = datas["block_position"]
    cordinates = Cordinates(position=position, pixel_offset=grid_pixel_offset)
    movementmanager = MovementManager(move_datas, spritesheet, cordinates)
    name = datas["name"]
    return Player(name, movementmanager, input_buffer, cordinates)


def build_scrolling(camera, level_datas):
    hard_boundary = Rect(*level_datas["boundary"])
    soft_boundaries = [Rect(*b) for b in level_datas["soft_boundaries"]]
    return Scrolling(
        camera,
        soft_boundaries=soft_boundaries,
        hard_boundary=hard_boundary,
        target_offset=level_datas["target_offset"])


def build_scene(level_datas, input_buffer):
    camera = Camera()
    scrolling = build_scrolling(camera, level_datas)
    scene = Scene(camera=camera, scrolling=scrolling)
    check_first_layer(level_datas)
    layer = None
    for element in level_datas["elements"]:
        if element.get("type") == ELEMENT_TYPE.LAYER:
            layer = Layer(element["name"], element["elevation"], [])
            scene.layers.append(layer)
            continue
        if element.get("type") == ELEMENT_TYPE.STATIC:
            static = build_static_element(element)
            layer.append(static)
        if element.get("type") == "player":
            offset = level_datas["grid_pixel_offset"]
            player = build_player(element, offset, input_buffer)
            layer.append(player.movement_manager)
            scene.players.append(player)
            if player.name == level_datas["scroll_target"]:
                scrolling.target = player.cordinates
    return scene
