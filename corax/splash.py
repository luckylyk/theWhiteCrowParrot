"""This is the Corax Engine hardcoded splash screen animation"""


import os
from itertools import cycle

import corax.context as cctx
from corax.core import COLORS
from corax.renderengine.draw import draw_image, draw_background
from corax.renderengine.io import load_frames, load_image
from corax.soundengine.io import load_sound, play_sound


LOGO_PATH = os.path.join(cctx.RESSOURCES_FOLDER, "logo.png")
CORAX_PATH = os.path.join(cctx.RESSOURCES_FOLDER, "corax_engine.png")
TITLE_PATH = os.path.join(cctx.RESSOURCES_FOLDER, "cinematic_platformer.png")
SOUND_PATH = os.path.join(cctx.RESSOURCES_FOLDER, "corax.ogg")
DURATION = 45
PLAY_SOUND_AT = 10
SPLASH_FPS = 15
FADE_LENGHT = 8
LOGO_SIZE = (143, 150)


def splash_screen(screen):
    frame = 0
    key = COLORS.GREEN

    logo_images = load_frames(LOGO_PATH, LOGO_SIZE, key, relative=False)[:5]
    corax_image = load_image(CORAX_PATH, key_color=COLORS.BLACK)
    title_image = load_image(TITLE_PATH, key_color=COLORS.BLACK)
    sound = load_sound(SOUND_PATH)

    images_iterator = cycle(logo_images)
    x = (LOGO_SIZE[0] / 2) + (cctx.RESOLUTION[0] / 2) - LOGO_SIZE[0]
    y = (LOGO_SIZE[1] / 2) + (cctx.RESOLUTION[1] / 2.5) - LOGO_SIZE[1]
    while frame < DURATION:
        if frame == PLAY_SOUND_AT:
            play_sound(sound)
        frame += 1
        logo_image = next(images_iterator)
        draw_background(screen, COLORS.BLACK)
        alpha = compute_fade_alpha(frame, DURATION, FADE_LENGHT)
        draw_image(logo_image, screen, (x, y), alpha=alpha)
        draw_image(corax_image, screen, (x - 25, y + 135), alpha=alpha)
        draw_image(title_image, screen, (x, y + 170), alpha=alpha)
        yield
    draw_background(screen, COLORS.BLACK)


def compute_fade_alpha(frame, duration, fade_length):
    if fade_length <= frame <= (duration - fade_length):
        return 255
    elif fade_length > frame:
        return 255 * (frame / fade_length)
    else:
        frame = fade_length - (frame - (duration - fade_length))
        return 255 * (frame / fade_length)
