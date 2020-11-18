import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import pygame
from whitecrow.prefs import OPTIONS
from whitecrow.gamepad import InputBuffer
from whitecrow.moves import filter_moves, filter_unholdable_moves, MovementManager
from whitecrow.animation import SpriteSheet
from whitecrow.cordinates import Cordinates


BG_PATH = r"D:\Works\Python\GitHub\pygame_game\data\background\screen010bis.png"
DATA_PATH = r"D:\Works\Python\GitHub\pygame_game\data\moves\whitecrowparrot_sword.json"

with open(DATA_PATH, 'r') as f:
    datas = json.load(f)

done = False
print(OPTIONS["resolution"])
screen = pygame.display.set_mode(OPTIONS["resolution"])#, pygame.FULLSCREEN)
pygame.display.set_caption("the White Crow Parrot")
clock = pygame.time.Clock()
pygame.joystick.init()
input_buffer = InputBuffer()
spritesheet = SpriteSheet.from_datafile(DATA_PATH)
cordinates = Cordinates(position=[10, 9], pixel_offset=[0, 10])
movementmanager = MovementManager(datas, spritesheet, cordinates)

bg = pygame.image.load(BG_PATH).convert()


while not done:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    done = joystick.get_button(7) == 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keystate_changed = input_buffer.update(joystick, cordinates.mirror)
    if keystate_changed is True:
        moves = filter_moves(datas, input_buffer)
        unholdable = filter_unholdable_moves(datas, input_buffer)
        movementmanager.unhold(unholdable)
        movementmanager.propose_moves(moves)

    movementmanager.next()
    screen.fill((0, 80, 180))
    screen.blit(bg, (0, 0))
    player_position = cordinates.world_position()
    screen.blit(movementmanager.current_image, player_position)

    clock.tick(OPTIONS["fps"])
    pygame.display.flip()
