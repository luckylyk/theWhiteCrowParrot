import json
from whitecrow.moves import filter_moves, filter_unholdable_moves, MovementManager
from whitecrow.animation import SpriteSheet
from whitecrow.cordinates import Cordinates
from whitecrow.gamepad import InputBuffer


class Player():
    def __init__(self, name, movement_manager, input_buffer, cordinates):
        self.input_buffer = input_buffer
        self.movement_manager = movement_manager
        self.cordinates = cordinates
        self.name = name

    @staticmethod
    def from_file(filename, name, start_position, pixel_offset, mirror=False):
        cordinates = Cordinates(start_position, pixel_offset, mirror)
        input_buffer = InputBuffer()
        spritesheet = SpriteSheet.from_datafile(filename)
        with open(filename, 'r') as f:
            datas = json.load(f)
        movement_manager = MovementManager(datas, spritesheet, cordinates)
        return Player(name, movement_manager, input_buffer, cordinates)

    def update_inputs(self, joystick):
        mirror = self.cordinates.mirror
        datas = self.movement_manager.datas
        keystate_changed = self.input_buffer.update(joystick, mirror)
        if keystate_changed is False:
            return

        moves = filter_moves(datas, self.input_buffer)
        unholdable = filter_unholdable_moves(datas, self.input_buffer)
        self.movement_manager.unhold(unholdable)
        self.movement_manager.propose_moves(moves)

    def next(self):
        self.movement_manager.next()

    @property
    def image(self):
        return self.movement_manager.image
