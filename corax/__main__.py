import os
import json
import pygame
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

if not sys.argv:
    raise ValueError("No game data folder specified as first argument")

import corax.context as cctx
from corax.theatre import Theatre

game = cctx.initialize(sys.argv[1])

clock = pygame.time.Clock()
pygame.joystick.init()
pygame.mixer.init()

screen = pygame.display.set_mode(
    cctx.RESOLUTION,
    pygame.SCALED)

theatre = Theatre(game)
pygame.display.set_caption(theatre.caption)

joystick = pygame.joystick.Joystick(0)

changeable = True
i = 0
done = False
while not done:
    joystick.init()

    done = joystick.get_button(7) == 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    for player in theatre.scene.players:
        player.update_inputs(joystick)
    for element in theatre.scene.evaluables:
        element.next()
    theatre.scene.render(screen)

    theatre.scene.scrolling.next()
    clock.tick(cctx.FPS)

    if "select" in player.input_buffer.pressed_delta() and changeable:
        changeable = False
        theatre.next()
    pygame.display.flip()
    i += 1
