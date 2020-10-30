from whitecrow.options import OPTIONS


class Player():
    def __init__(self, animationsheet=None, position=None):
        self.position = position or [0, 0]
        self.animationsheet = animationsheet
        self.animationsheet.block_offset_requested.connect(self.do_blockoffset)

        self.jump = False
        self.crouch = False
        self.high_hit = False
        self.low_hit = False
        self.stroke = False
        self.high_block = False
        self.low_block = False
        self.forward = False
        self.backward = False
        self.dash = False

    def do_blockoffset(self, blockoffset):
        self.position[0] += blockoffset[0] * OPTIONS["grid_size"]
        self.position[1] += blockoffset[1] * OPTIONS["grid_size"]

    def set_joystick(self, joystick):
        self.jump = joystick.get_button(0) == 1
        self.crouch = joystick.get_hat(0)[1] == -1
        self.high_hit = joystick.get_button(4) == 1
        self.low_hit = joystick.get_button(5) == 1
        self.stroke = self.high_hit and self.low_hit
        self.high_block = joystick.get_axis(2) > .5
        self.low_block = joystick.get_axis(2) < -.5
        self.forward = joystick.get_hat(0)[0] == 1
        self.backward = joystick.get_hat(0)[0] == -1
        self.dash = joystick.get_button(1) == 1

    def set_animation(self):
        if self.animationsheet.locked is True:
            if self.low_hit and self.animationsheet.is_playing("crouch_down"):
                self.animationsheet.set_animation("crouch_hit_shoot")
            return

        if self.jump:
            self.animationsheet.set_animation("jump")
        elif self.forward:
            self.animationsheet.set_animation("step_forward")
        elif self.dash:
            self.animationsheet.set_animation("back_dash")
        elif self.backward:
            self.animationsheet.set_animation("step_backward")
        elif self.crouch:
            self.animationsheet.set_animation("crouch_down")
        elif self.stroke:
            self.animationsheet.set_animation("stroke_ready")
        elif self.high_hit:
            self.animationsheet.set_animation("high_hit_ready")
        elif self.low_hit:
            self.animationsheet.set_animation("low_hit_ready")
        elif self.high_block:
            self.animationsheet.set_animation("high_block")
        elif self.low_block:
            self.animationsheet.set_animation("low_block")

    def unhold_check(self):
        sheet = self.animationsheet
        if self.crouch is False and sheet.is_playing("crouch_down"):
            sheet.hold = False
        elif self.stroke is False and sheet.is_playing("stroke_ready"):
            sheet.hold = False
        elif self.high_hit is False and sheet.is_playing("high_hit_ready"):
            sheet.hold = False
        elif self.low_hit is False and sheet.is_playing("low_hit_ready"):
            sheet.hold = False
        elif self.high_hit is False and sheet.is_playing("crouch_hit_shoot"):
            sheet.hold = False
        elif self.high_block is False and sheet.is_playing("high_block"):
            sheet.hold = False
        elif self.low_block is False and sheet.is_playing("low_block"):
            sheet.hold = False