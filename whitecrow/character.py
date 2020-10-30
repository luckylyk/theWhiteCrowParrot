from whitecrow.options import OPTIONS


class Player():
    def __init__(self, move_sheet=None, position=None, gamepad_buffer=None):
        self.position = position or [0, 0]
        self.gamepad_buffer = gamepad_buffer
        self.move_sheet = move_sheet
        self.move_sheet.block_offset_requested.connect(self.do_blockoffset)
        self.move_sheet.do_mirror.connect(self.do_mirror)
        self.mirror = False

    def do_mirror(self):
        self.mirror = not self.mirror
        self.move_sheet.mirror = self.mirror

    def do_blockoffset(self, blockoffset):
        self.position[0] += blockoffset[0] * OPTIONS["grid_size"]
        self.position[1] += blockoffset[1] * OPTIONS["grid_size"]

    def set_move(self):
        if self.move_sheet.locked is True:
            return
        for move, data in self.move_sheet.iter_move_datas():
            conditions = data.get("conditions")
            if not conditions:
                continue
            moves = conditions.get("moves")
            if moves and move not in moves:
                continue
            inputs = get_move_inputs(data, mirror=self.mirror)
            if not inputs:
                continue
            if data.get("loop"):
                inputs2 = self.gamepad_buffer.inputs()
            else:
                inputs2 = self.gamepad_buffer.pressed_delta()
            if all(i in inputs2 for i in inputs):
                print(inputs)
                self.move_sheet.set_move(move)

    def unhold_check(self):
        conditions = self.move_sheet.move_data.get("conditions")
        if not conditions:
            return
        inputs = get_move_inputs(self.move_sheet.move_data, self.mirror)
        if not inputs:
            return
        if all(i in self.gamepad_buffer.released_delta() for i in inputs):
            self.move_sheet.hold = False


def get_move_inputs(move_data, mirror=False):
    conditions = move_data.get("conditions")
    if not conditions:
        return
    if mirror is False:
        return conditions.get("inputs")
    inputs = conditions.get("reverted_inputs")
    if not inputs:
        return conditions.get("inputs")
    return inputs