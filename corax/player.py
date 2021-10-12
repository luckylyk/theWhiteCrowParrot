import json
import os
import logging

import corax.context as cctx
from corax.animation import SpriteSheet
from corax.controller import AnimationController
from corax.coordinate import Coordinate, to_block_position
from corax.euclide import points_to_vector
from corax.mathutils import sum_num_arrays
from corax.pygameutils import render_image
from corax.sequence import (
    filter_moves_by_inputs, filter_unholdable_moves,
    build_sequence_to_destination)


class PlayerSlot():
    """
    This class is a reference to the player at the scene lever.
    Player is living at the theatre level and the object status is kept through
    the scene switch. But to locate the player in the scene (layer lever and
    appearing spots) we need this reference object.
    The link between Player and his PlayerSlot is done after the theatre build
    a new scene using the names. A player must hold the same name than his slot
    to be linked.
    The argument positions is a dict containing the player popping spot as
    block position. The key of that dictionnary is the name of the spot, which
    can use in crackle to define the character position.
    """
    def __init__(self, name, block_position, flip):
        self.name = name
        self.block_position = block_position
        self.flip = flip
        self.player = None
        self.visible = True

    def render(self, screen, deph, camera):
        self.player.render(screen, deph, camera)

    def evaluate(self):
        self.player.animation_controller.evaluate()

    @property
    def coordinate(self):
        return self.player.coordinate


class Player():
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.layers = data["layers"]
        self.coordinate = Coordinate()
        self.animation_controller = build_player_animation_controller(data, self.coordinate)

    def set_no_go_zones(self, zones):
        self.animation_controller.no_go_zones = zones

    def input_updated(self, input_buffer):
        data = self.animation_controller.data
        moves = filter_moves_by_inputs(data, input_buffer, self.flip)
        unholdable = filter_unholdable_moves(data, input_buffer, self.flip)
        self.animation_controller.unhold(unholdable)
        self.animation_controller.propose_moves(moves)
        if cctx.DEBUG:
            logging.debug(f"Proposed moves: {moves}")

    def evaluate(self):
        self.animation_controller.evaluate()

    def render(self, screen, deph, camera):
        deph = deph + self.deph
        position = camera.relative_pixel_position(self.pixel_position, deph)
        for image in self.animation_controller.images:
            render_image(image, screen, position)

    def set_sheet(self, sheet_name):
        sheet_filename = self.data["sheets"][sheet_name]
        layers = [layer for layer, state in self.layers.items() if state]
        self.animation_controller.set_sheet(sheet_filename, layers)

    def set_layer_visible(self, layer, state):
        self.layers[layer] = state
        if state and layer not in self.animation_controller.layers:
            self.animation_controller.layers.append(layer)
        elif not state and layer in self.animation_controller.layers:
            self.animation_controller.layers.remove(layer)

    def reach(self, destination, moves):
        self.animation_controller.flush()
        sequence = build_sequence_to_destination(
            moves=moves,
            data=self.animation_controller.data,
            coordinate=self.coordinate,
            dst=destination)
        self.animation_controller.sequence = sequence
        return sequence

    def pin(self):
        vector = points_to_vector(
            self.animation.pixel_center,
            self.animation.centers[0])
        offset = to_block_position(vector)
        position = sum_num_arrays(self.coordinate.block_position, offset)
        self.coordinate.block_position = position

    @property
    def pixel_center(self):
        if None in [self.animation.pixel_center, self.coordinate.pixel_position]:
            return
        return sum_num_arrays(
            self.animation.pixel_center, self.coordinate.pixel_position)

    @property
    def sheet_name(self):
        for name, filename in self.data["sheets"].items():
            if filename == self.animation_controller.spritesheet.name:
                return name

    @property
    def trigger(self):
        return self.animation_controller.trigger

    @property
    def animation(self):
        return self.animation_controller.animation

    @property
    def hitboxes(self):
        return self.animation.hitboxes

    @property
    def hitbox_colors(self):
        return self.data["hitboxes_color"]

    @property
    def pixel_position(self):
        return self.coordinate.pixel_position

    @property
    def deph(self):
        return self.coordinate.deph

    @property
    def flip(self):
        return self.coordinate.flip


def build_player_animation_controller(data, coordinate):
    """
    Build Animation Controller from player data. It creates the startup
    SpriteSheet from the default sheet define in the player's data.
    """
    filename = data["sheets"][data["default_sheet"]]
    data_path = os.path.join(cctx.SHEET_FOLDER, filename)
    with open(data_path, "r") as f:
        sheet_data = json.load(f)
    spritesheet = SpriteSheet.from_filename(filename, data_path)
    layers = [str(key) for key in data["layers"] if data["layers"][key]]
    return AnimationController(sheet_data, spritesheet, coordinate, layers)


def load_players():
    """
    Load player found from the game player folder.
    """
    player_files = os.listdir(cctx.PLAYER_FOLDER)
    filenames = [os.path.join(cctx.PLAYER_FOLDER, f) for f in player_files]
    players = []
    for filename in filenames:
        with open(filename, "r") as f:
            data = json.load(f)
        player = Player(data)
        players.append(player)
    return players
