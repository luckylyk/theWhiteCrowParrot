
from corax import config


# Set default keybinding
BINDING = {
    'A': 'A',
    'B': 'B',
    'X': 'X',
    'Y': 'Y',
    'L1': 'L1',
    'L2': 'L2',
    'R1': 'R1',
    'R2': 'R2',
    'start': 'start',
    'select': 'select',
    'LSB': 'LSB',
    'RSB': 'RSB',
    'UP': 'UP',
    'DOWN': 'DOWN',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
    'RS_LEFT': 'RS_LEFT',
    'RS_RIGHT': 'RS_RIGHT'
}


GAME_DEFAULT_COMMANDS = {k: False for k in BINDING}


REVERSE_BINDING = {
    BINDING['RIGHT']: BINDING['LEFT'],
    BINDING['LEFT']: BINDING['RIGHT'],
    BINDING['RS_RIGHT']: BINDING['RS_LEFT'],
    BINDING['RS_LEFT']: BINDING['RS_RIGHT']
}


def get_keystate(key_name, joystick):
    match key_name:
        case "A":
            return joystick.get_button(0) == 1
        case 'B':
            return joystick.get_button(1) == 1
        case 'X':
            return joystick.get_button(2) == 1
        case 'Y':
            return joystick.get_button(3) == 1
        case 'L1':
            return joystick.get_button(4) == 1
        case 'L2':
            return joystick.get_axis(4) > .5
        case 'R1':
            return joystick.get_button(5) == 1
        case 'R2':
            return joystick.get_axis(5) > .5
        case 'select':
            return joystick.get_button(6) == 1
        case 'start':
            return joystick.get_button(7) == 1
        case 'LSB':
            return joystick.get_button(8) == 1
        case 'RSB':
            return joystick.get_button(9) == 1
        case 'UP':
            return joystick.get_hat(0)[1] == 1 or joystick.get_axis(1) < -.5
        case 'DOWN':
            return joystick.get_hat(0)[1] == -1 or joystick.get_axis(1) > .5
        case 'LEFT':
            return joystick.get_hat(0)[0] == -1 or joystick.get_axis(0) < -.5
        case 'RIGHT':
            return joystick.get_hat(0)[0] == 1 or joystick.get_axis(0) > .5
        case 'RS_LEFT':
            return joystick.get_axis(2) < -.5
        case 'RS_RIGHT':
            return joystick.get_axis(2) > .5
    raise KeyError(f'Unknown key {key_name}')


def load_config_keybinding():
    BINDING['A'] = config.get('keybinding')['A']
    BINDING['B'] = config.get('keybinding')['B']
    BINDING['X'] = config.get('keybinding')['X']
    BINDING['Y'] = config.get('keybinding')['Y']
    BINDING['L1'] = config.get('keybinding')['L1']
    BINDING['L2'] = config.get('keybinding')['L2']
    BINDING['R1'] = config.get('keybinding')['R1']
    BINDING['R2'] = config.get('keybinding')['R2']
    BINDING['start'] = config.get('keybinding')['start']
    BINDING['select'] = config.get('keybinding')['select']
    BINDING['LSB'] = config.get('keybinding')['LSB']
    BINDING['RSB'] = config.get('keybinding')['RSB']
    BINDING['UP'] = config.get('keybinding')['UP']
    BINDING['DOWN'] = config.get('keybinding')['DOWN']
    BINDING['LEFT'] = config.get('keybinding')['LEFT']
    BINDING['RIGHT'] = config.get('keybinding')['RIGHT']
    BINDING['RS_LEFT'] = config.get('keybinding')['RS_LEFT']
    BINDING['RS_RIGHT'] = config.get('keybinding')['RS_RIGHT']

    REVERSE_BINDING[config.get('RIGHT')] = config.get('LEFT')
    REVERSE_BINDING[config.get('LEFT')] = config.get('RIGHT')
    REVERSE_BINDING[config.get('RS_RIGHT')] = config.get('RS_LEFT')
    REVERSE_BINDING[config.get('RS_LEFT')] = config.get('RS_RIGHT')


def get_current_commands(joystick):
    return {
        'A': get_keystate(BINDING['A'], joystick),
        'B': get_keystate(BINDING['B'], joystick),
        'X': get_keystate(BINDING['X'], joystick),
        'Y': get_keystate(BINDING['Y'], joystick),
        'L1': get_keystate(BINDING['L1'], joystick),
        'L2': get_keystate(BINDING['L2'], joystick),
        'R1': get_keystate(BINDING['R1'], joystick),
        'R2': get_keystate(BINDING['R2'], joystick),
        'select': get_keystate(BINDING['select'], joystick),
        'start': get_keystate(BINDING['start'], joystick),
        'LSB': get_keystate(BINDING['LSB'], joystick),
        'RSB': get_keystate(BINDING['RSB'], joystick),
        'UP': get_keystate(BINDING['UP'], joystick),
        'DOWN': get_keystate(BINDING['DOWN'], joystick),
        'LEFT': get_keystate(BINDING['LEFT'], joystick),
        'RIGHT': get_keystate(BINDING['RIGHT'], joystick),
        'RS_LEFT': get_keystate(BINDING['RS_LEFT'], joystick),
        'RS_RIGHT': get_keystate(BINDING['RS_RIGHT'], joystick)
    }


def reverse_buttons(buttons):
    return [REVERSE_BINDING.get(button, button) for button in buttons]


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
