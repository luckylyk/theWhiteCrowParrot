import os
import json
import pygame
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

if not sys.argv:
    raise ValueError("No game data folder specified as first argument")

from whitecrow import constants
constants.populate(sys.argv[1])

from whitecrow.prefs import PREFS
from whitecrow.constants import GAME_FILE
from whitecrow.theatre import Theatre


with open(GAME_FILE) as f:
    game = json.load(f)


clock = pygame.time.Clock()
pygame.joystick.init()
pygame.mixer.init()

screen = pygame.display.set_mode(PREFS["resolution"], pygame.SCALED | pygame.FULLSCREEN)

theatre = Theatre(game)
pygame.display.set_caption(theatre.caption)

joystick = pygame.joystick.Joystick(0)
joystick.init()

i = 0
done = False
while not done:

    done = joystick.get_button(7) == 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill((100, 195, 255))
    if i % 2 == 0:
        for player in theatre.scene.players:
            player.update_inputs(joystick)
            player.next()
        for particles in theatre.scene.particles:
            particles.next()
    theatre.scene.scrolling.next()
    theatre.scene.render(screen)
    clock.tick(PREFS["fps"] * 2)

    pygame.display.flip()
    i += 1
