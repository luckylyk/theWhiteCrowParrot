

class Signal():
    def __init__(self):
        self._functions = []

    def emit(self, *args, **kwargs):
        for func in self._functions:
            func(*args, **kwargs)

    def connect(self, func):
        self._functions.append(func)


class EVENTS():
    FLIP = "flip"
    BLOCK_OFFSET = "block_offset"