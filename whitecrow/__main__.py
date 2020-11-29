import os
import json
import pygame
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from whitecrow.prefs import PREFS
from whitecrow.constants import LEVEL_FOLDER, SOUNDS_FOLDER
from whitecrow.gamepad import InputBuffer
from whitecrow.cordinates import Cordinates
from whitecrow.scene import build_scene
from whitecrow.camera import Camera, Scrolling
from whitecrow.euclide import Rect
from whitecrow.player import Player


done = False
screen = pygame.display.set_mode(PREFS["resolution"], pygame.FULLSCREEN)
pygame.display.set_caption("the White Crow Parrot")
clock = pygame.time.Clock()
pygame.joystick.init()
input_buffer = InputBuffer()

LEVEL_FILE = os.path.join(LEVEL_FOLDER, "level_01.json")
with open(LEVEL_FILE, 'r') as f:
    level = json.load(f)
scene = build_scene(level, input_buffer)

pygame.mixer.init()
SOUND_FILE = os.path.join(SOUNDS_FOLDER, "ambiances", "nature1.ogg")
music = pygame.mixer.Sound(SOUND_FILE)
music.play(-1)
SOUND_FILE = os.path.join(SOUNDS_FOLDER, "musics", "saqueboute.ogg")
music = pygame.mixer.Sound(SOUND_FILE)
music.play(-1)


i = 0
while not done:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    done = joystick.get_button(7) == 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill((100, 195, 255))
    if i % 2 == 0:
        for player in scene.players:
            player.update_inputs(joystick)
            player.next()
    scene.scrolling.next()
    scene.render(screen)
    clock.tick(PREFS["fps"] * 2)

    pygame.display.flip()
    i += 1
