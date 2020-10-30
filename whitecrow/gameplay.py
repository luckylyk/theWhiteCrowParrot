# module currently unused

JOYSTICK_DEFAULT_STATES = {
    "buttons": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # A, B, X, Y, L, R, select, start, LSB, RSB
    "left_stick_axes": [0.0, 0.0],
    "right_stick_axes": [0.0, 0.0],
    "trigger_axe": 0.0,
    "dpad": [0, 0]
}


def build_default_joystick_state():
    states = {}
    for key, item in JOYSTICK_DEFAULT_STATES.items():
        if not isinstance(list, item):
            states[key] = item
            continue
        states[key] = item.copy()
    return states


def get_current_joystick_state(joystick):
    return {
    "buttons": [joystick.get_button(i) for i in range(10)],
    "left_stick_axes": [joystick.get_axis(i) for i in range(2)],
    "right_stick_axes": [joystick.get_axis(i) for i in range(3, 5)],
    "trigger_axe": joystick.get_axis(2),
    "dpad": joystick.get_hat(0)}


def get_current_commands(joystick):
    return {
        "A": joystick.get_button(0),
        "B": joystick.get_button(1),
        "X": joystick.get_button(2),
        "Y": joystick.get_button(3),
        "L1": joystick.get_button(3),
        "L2": joystick.get_axis(2) > .5,
        "R1": joystick.get_button(4),
        "L2": joystick.get_axis(2) < -.5,
        "select": joystick.get_button(5),
        "start": joystick.get_button(6),
        "LSB": joystick.get_button(7),
        "RSB": joystick.get_button(8),
        "UP": joystick.get_hat(0)[1] == 1 or joystick.get_axis(1) > .5,
        "DOWN":  joystick.get_hat(0)[1] == -1 or joystick.get_axis(1) < -.5,
        "LEFT": joystick.get_hat(0)[0] == -1 or joystick.get_axis(0) < -.5,
        "RIGHT": joystick.get_hat(0)[0] == 1 or joystick.get_axis(0) > .5,
        "RS_LEFT": joystick.get_axis(4) < -.5,
        "RS_RIGHT": joystick.get_axis(4) > .5}


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
    "UP": False,
    "DOWN": False,
    "LEFT": False,
    "RIGHT": False,
    "RS_LEFT": False,
    "RS_RIGHT": False,
}