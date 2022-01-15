

GAME_DEFAULT_COMMANDS = {
    "A": False,
    "B": False,
    "X": False,
    "Y": False,
    "L1": False,
    "L2": False,
    "R1": False,
    "R2": False,
    "start": False,
    "select": False,
    "LSB": False,
    "RSB": False,
    "UP": False,
    "DOWN": False,
    "LEFT": False,
    "RIGHT": False,
    "RS_LEFT": False,
    "RS_RIGHT": False
}


def get_current_commands(joystick):
    return {
        "A": joystick.get_button(0) == 1,
        "B": joystick.get_button(1) == 1,
        "X": joystick.get_button(2) == 1,
        "Y": joystick.get_button(3) == 1,
        "L1": joystick.get_button(4) == 1,
        "L2": joystick.get_axis(4) > .5,
        "R1": joystick.get_button(5) == 1,
        "R2": joystick.get_axis(5) > .5,
        "select": joystick.get_button(6) == 1,
        "start": joystick.get_button(7) == 1,
        "LSB": joystick.get_button(8) == 1,
        "RSB": joystick.get_button(9) == 1,
        "UP": joystick.get_hat(0)[1] == 1 or joystick.get_axis(1) < -.5,
        "DOWN": joystick.get_hat(0)[1] == -1 or joystick.get_axis(1) > .5,
        "LEFT": joystick.get_hat(0)[0] == -1 or joystick.get_axis(0) < -.5,
        "RIGHT": joystick.get_hat(0)[0] == 1 or joystick.get_axis(0) > .5,
        "RS_LEFT": joystick.get_axis(2) < -.5,
        "RS_RIGHT": joystick.get_axis(2) > .5}


REVERSE_MAPPING = {
    "RIGHT": "LEFT",
    "LEFT": "RIGHT",
    "RS_RIGHT": "RS_LEFT",
    "RS_LEFT": "RS_RIGHT"
}


def reverse_buttons(buttons):
    return [REVERSE_MAPPING.get(button, button) for button in buttons]


class InputBuffer():
    def __init__(self):
        self.old_states = GAME_DEFAULT_COMMANDS.copy()
        self.current_states = GAME_DEFAULT_COMMANDS.copy()
        self.buffer_key_pressed = []

    def flush(self):
        self.buffer_key_pressed = []

    def update(self, joystick):
        joystick.init()
        states = get_current_commands(joystick)
        if states == self.current_states:
            return False
        self.old_states = self.current_states
        self.current_states = states
        self.buffer(joystick)
        return True

    def buffer(self, joystick):
        states = get_current_commands(joystick)
        for k, v in states.items():
            if v is True and k not in self.buffer_key_pressed:
                self.buffer_key_pressed.append(k)

    def pressed_delta(self):
        return [
            k for k, v in self.current_states.items()
            if self.old_states[k] is False and v is True]

    def released_delta(self):
        return [
            k for k, v in self.current_states.items()
            if self.old_states[k] is True and v is False]

    def inputs(self):
        return [k for k, v in self.current_states.items() if v is True]

