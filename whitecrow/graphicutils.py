
import os
import pygame
from whitecrow.iterators import itertable
from whitecrow.options import ANIMATION_FOLDER


def load_images(filename, block_size, key_color):
    filename = os.path.join(ANIMATION_FOLDER, filename)
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


def image_mirror(image, horizontal=True, vertical=False):
    return pygame.transform.flip(image, horizontal, vertical)