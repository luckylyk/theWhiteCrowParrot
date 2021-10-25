
import pygame
import corax.context as cctx


SCREEN = None
USE_LETTERBOX = False
LETTERBOX_OFFSET = None
HIGH_LETTERBOX = None
LOW_LETTERBOX = None


def initialize_screen_variables(screen):
    if not cctx.RESOLUTION:
        raise RuntimeError(
            "Screen size can't be initialized if before corax."
            "Run corax.context.initialize() function first")
    global LETTERBOX_OFFSET, HIGH_LETTERBOX, LOW_LETTERBOX, USE_LETTERBOX,\
        SCREEN

    height = screen.get_size()[1]
    if height == cctx.RESOLUTION[1]:
        SCREEN = cctx.RESOLUTION
        return
    SCREEN = screen.get_size()
    USE_LETTERBOX = True
    LETTERBOX_OFFSET = (height / 2) - (cctx.RESOLUTION[1] / 2)
    HIGH_LETTERBOX = 0, 0, cctx.RESOLUTION[0], LETTERBOX_OFFSET + 1
    bottom_letterbox_top = LETTERBOX_OFFSET + cctx.RESOLUTION[1] - 1
    LOW_LETTERBOX = 0, bottom_letterbox_top, cctx.RESOLUTION[0], LETTERBOX_OFFSET + 1


def setup_display(scaled=True, fullscreen=True):
    screen_mode_flags = 0
    if scaled:
        screen_mode_flags |= pygame.SCALED
    if fullscreen:
        screen_mode_flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(cctx.RESOLUTION, screen_mode_flags)
    initialize_screen_variables(screen)
    pygame.display.set_caption(cctx.TITLE)
    pygame.mouse.set_visible(False)
    return screen


def screen_relative_y(y):
    if not USE_LETTERBOX:
        return y
    return y + LETTERBOX_OFFSET