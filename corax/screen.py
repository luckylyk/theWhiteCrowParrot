
import corax.context as cctx


SCREEN = None
USE_LETTERBOX = False
TOP_LETTERBOX = None
BOTTOM_LETTERBOX = None
LEFT_LETTERBOX = None
RIGHT_LETTERBOX = None


def initialize_screen(size):
    if not cctx.RESOLUTION:
        raise RuntimeError(
            "Screen size can't be initialized before corax context."
            "Run corax.context.initialize() function first")
    global \
        TOP_LETTERBOX, BOTTOM_LETTERBOX, LEFT_LETTERBOX, RIGHT_LETTERBOX, \
        USE_LETTERBOX, SCREEN

    SCREEN = size
    USE_LETTERBOX = cctx.RESOLUTION != cctx.RENDER_AREA
    if not USE_LETTERBOX:
        return
    if cctx.RESOLUTION[1] != cctx.RENDER_AREA[1]:
        bottom = int((cctx.RESOLUTION[1] - cctx.RENDER_AREA[1]) / 2)
        TOP_LETTERBOX = 0, 0, SCREEN[0], bottom
        BOTTOM_LETTERBOX = 0, SCREEN[1] - bottom, SCREEN[0], SCREEN[1]
    if cctx.RESOLUTION[0] != cctx.RENDER_AREA[0]:
        right = int((cctx.RESOLUTION[0] - cctx.RENDER_AREA[0]) / 2)
        LEFT_LETTERBOX = 0, 0, right, SCREEN[1]
        RIGHT_LETTERBOX = SCREEN[0] - right, 0, SCREEN[0], SCREEN[1]


def map_to_render_area(x, y):
    if not USE_LETTERBOX:
        return [x, y]
    offset_x = int((cctx.RESOLUTION[0] - cctx.RENDER_AREA[0]) / 2)
    offset_y = int((cctx.RESOLUTION[1] - cctx.RENDER_AREA[1]) / 2)
    return [x + offset_x, y + offset_y]