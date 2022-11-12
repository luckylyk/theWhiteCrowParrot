import os
import logging

import corax.context as cctx
from corax.animation import SpriteSheet
from corax.controller import AnimationController
from corax.coordinate import Coordinate, to_block_position, flip_position
from corax.core import EVENTS
from corax.euclide import points_to_vector
from corax.mathutils import sum_num_arrays
from corax.override import load_json
from corax.sequence import (
    filter_moves_by_inputs, filter_unholdable_moves,
    build_sequence_to_destination)


class CharacterSlot:
    """
    This class is a reference to the character at the scene lever.
    Player is living at the theatre level and the object status is kept through
    the scene switch. But to locate the character in the scene (layer lever and
    appearing spots) we need this reference object.
    The link between Player and his PlayerSlot is done after the theatre build
    a new scene using the names. A character must hold the same name than his
    slot to be linked.
    The argument positions is a dict containing the character popping spot as
    block position. The key of that dictionnary is the name of the spot, which
    can use in crackle to define the character position.
    """
    def __init__(self, name, block_position, flip):
        self.name = name
        self.block_position = block_position
        self.flip = flip
        self.character = None
        self.visible = True

    def evaluate(self):
        self.character.evaluate()

    @property
    def coordinate(self):
        return self.character.coordinate


class Character:
    def __init__(self, data):
        self.data = data
        self.coordinate = Coordinate()
        self.animation_controller = build_character_animation_controller(
            data, self.coordinate)

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
        if not sequence:
            return sequence
        self.animation_controller.set_move(sequence[0])
        if len(sequence) == 1:
            return sequence
        self.animation_controller.sequence = sequence[1:]
        return sequence

    def pin(self):
        """
        Pin an object is usefull to move a character in a middle of an
        animation. This is generally combined with a flush which set the
        default animation of the current sheet, flushing the event supposed to
        be triggered at animation end.
        For instance, this is usefull to interupt a walk or run cycle.
        """
        point1 = self.animation.pixel_center
        point2 = self.animation.centers[0]
        if None in (point1, point2):
            logging.debug(f"Pin {self.name}: skipped")
            return
        pixel_vector = points_to_vector(point1, point2)
        # In rare particulare cases where a pre offset is has been proceeded,
        # this pre offset has to be substracted.
        pre_offset = animation_pre_offset(self.animation, self.coordinate.flip)
        offset = sum_num_arrays(to_block_position(pixel_vector), pre_offset)
        position = sum_num_arrays(self.coordinate.block_position, offset)
        self.coordinate.block_position = position
        logging.debug(f"Pin {self.name}: vertor({offset})")

    @property
    def pixel_center(self):
        pos = [self.animation.pixel_center, self.coordinate.pixel_position]
        if None in pos:
            return
        return sum_num_arrays(*pos)

    @property
    def sheet_name(self):
        for name, filename in self.data["sheets"].items():
            if filename == self.animation_controller.spritesheet.name:
                return name

    @property
    def name(self):
        return self.data["name"]

    @property
    def layers(self):
        return self.data["layers"]

    @property
    def type(self):
        return self.data["type"]

    @property
    def trigger(self):
        return self.animation_controller.trigger

    @property
    def animation(self):
        return self.animation_controller.animation

    @property
    def hitmaps(self):
        return self.animation.hitmaps

    @property
    def hitmap_colors(self):
        return self.data["hitmaps_color"]

    @property
    def pixel_position(self):
        return self.coordinate.pixel_position

    @property
    def deph(self):
        return self.coordinate.deph

    @property
    def flip(self):
        return self.coordinate.flip


def build_character_animation_controller(data, coordinate):
    """
    Build Animation Controller from character data. It creates the startup
    SpriteSheet from the default sheet define in the character's data.
    """
    filename = data["sheets"][data["default_sheet"]]
    data_path = os.path.join(cctx.SHEET_FOLDER, filename)
    sheet_data = load_json(data_path)
    spritesheet = SpriteSheet.from_filename(filename, data_path)
    layers = [str(key) for key in data["layers"] if data["layers"][key]]
    return AnimationController(sheet_data, spritesheet, coordinate, layers)


def load_characters():
    """
    Load player found from the game player folder.
    """
    return [
        Character(load_json(os.path.join(cctx.CHARACTER_FOLDER, filename)))
        for filename in os.listdir(cctx.CHARACTER_FOLDER)]


def animation_pre_offset(animation, flip):
    """
    Get the pre offset (block offset set before it starts) off an animation.
    """
    for key, value in animation.pre_events.items():
        if key == EVENTS.BLOCK_OFFSET:
            return flip_position(value) if not flip else value
    return (0, 0)