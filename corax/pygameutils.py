
"""
This module is the bridge to PyGame. It is supposed to be one the rare import
of it. It wrap the pygame functions to make them as much generic as possible
to make a futur engine change easy. It's mainly helper to get and load pygame
object from files.
"""


import os
import pygame
import corax.context as cctx
from corax.iterators import itertable


def setup_display(caption, args):
    screen_mode_flags = 0
    if "--scaled" in args or "-s" in args:
        screen_mode_flags |= pygame.SCALED
    if "--fullscreen" in args or "-f" in args:
        screen_mode_flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(cctx.RESOLUTION, screen_mode_flags)
    pygame.display.set_caption(caption)
    return screen


def escape_in_events(events):
    return any(
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        for event in events)


def load_images(filename, frame_size, key_color):
    filename = os.path.join(cctx.ANIMATION_FOLDER, filename)
    sheet = pygame.image.load(filename).convert()
    width, height = frame_size
    row = sheet.get_height() / height
    col = sheet.get_width() / width
    if row != int(row) or col != int(col):
        message = (
            "the sprite sheet file {} size doesn't match "
            "with his block size".format(filename))
        raise ValueError(message)
    images = []
    for j, i in itertable(int(row), int(col)):
        image = pygame.Surface([width, height]).convert()
        x, y = i * width, j * height
        image.blit(sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(key_color)
        images.append(image)
    return images


def load_image(filename, key_color=None):
    image = pygame.image.load(filename).convert()
    if key_color is not None:
        image.set_colorkey(key_color)
    return image


def image_mirror(image, horizontal=True, vertical=False):
    return pygame.transform.flip(image, horizontal, vertical)


def load_sound(filename):
    filename = os.path.join(cctx.SOUNDS_FOLDER, filename)
    return pygame.mixer.Sound(filename)


def render_image(image, screen, position, alpha=255):
    if alpha == 255:
        screen.blit(image, position)
        return
    # work around to blit with transparency found on here:
    # https://nerdparadise.com/programming/pygameblitopacity
    # thanks dude !
    x, y = position
    w, h = image.get_size()
    temp = pygame.Surface((w, h)).convert()
    temp.blit(screen, (-x, -y))
    temp.blit(image, (0, 0))
    temp.set_alpha(alpha)
    screen.blit(temp, position)


def render_rect(screen, color, x, y, width, height , alpha=255):
    temp = pygame.Surface((width, height)).convert()
    pygame.draw.rect(temp, color, [0, 0, width, height])
    temp.set_alpha(alpha)
    screen.blit(temp, (x, y))


def render_background(screen, color, alpha=255):
    render_rect(
        screen=screen,
        color=color,
        x=0,
        y=0,
        width=cctx.RESOLUTION[0],
        height=cctx.RESOLUTION[1],
        alpha=alpha)


def render_ellipse(screen, color, x, y, height, width):
    pygame.draw.ellipse(screen, color, [x, y, height, width])


def render_grid(screen, camera, color, alpha=255):
    temp = pygame.Surface(cctx.RESOLUTION).convert()
    # Render grid
    l = -camera.pixel_position[0] % cctx.BLOCK_SIZE
    while l < cctx.RESOLUTION[0]:
        pygame.draw.line(temp, color, (l, 0), (l, cctx.RESOLUTION[1]))
        l += cctx.BLOCK_SIZE
    t = 0
    while t < cctx.RESOLUTION[1]:
        pygame.draw.line(temp, color, (0, t), (cctx.RESOLUTION[0], t))
        t += cctx.BLOCK_SIZE
    temp.set_alpha(alpha)
    screen.blit(temp, (0, 0))


def render_text(screen, color, x, y, text, size=15, bold=False):
    font = pygame.font.SysFont('Consolas', size)
    font.bold = bold
    textsurface = font.render(text, False, color)
    screen.blit(textsurface, (x, y))


def render_centered_text(screen, text, color):
    font = pygame.font.SysFont('Consolas', 15)
    text = font.render(text, True, (255, 255, 255))
    x, y = cctx.RESOLUTION
    text_rect = text.get_rect(center=(x/2, y/2))
    screen.blit(text, text_rect)
