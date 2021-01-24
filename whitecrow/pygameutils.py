
import os
import pygame
import whitecrow.context as wctx
from whitecrow.iterators import itertable


def load_images(filename, block_size, key_color):
    filename = os.path.join(wctx.ANIMATION_FOLDER, filename)
    sheet = pygame.image.load(filename).convert()
    width, height = block_size
    row = sheet.get_height() / height
    col = sheet.get_width() / width
    if row != int(row) or col != int(col):
        raise ValueError(
            "the sprite sheet file size doesn't match with his block size")
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
    filename = os.path.join(wctx.SOUNDS_FOLDER, filename)
    return pygame.mixer.Sound(filename)


def render_image(image, screen, position, alpha=1):
    if alpha == 1:
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


def render_rect(screen, color, x, y, height, width):
    pygame.draw.rect(screen, color, [x, y, height, width])


def render_ellipse(screen, color, x, y, height, width):
    pygame.draw.ellipse(screen, color, [x, y, height, width])