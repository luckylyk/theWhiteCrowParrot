import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


import pygame
from whitecrow.options import OPTIONS, MOVE_FOLDER
from whitecrow.animation import MoveSheet
from whitecrow.graphicutils import load_images
from whitecrow.character import Player
from whitecrow.gameplay import GamepadBuffer


pygame.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
screen = pygame.display.set_mode(OPTIONS["resolution"], pygame.FULLSCREEN)
pygame.display.set_caption("the White Crow Parrot")
clock = pygame.time.Clock()


WHITECROWPARROT_SWORD_PATH = os.path.join(MOVE_FOLDER, "whitecrowparrot_sword.json")
sheet = MoveSheet.from_json(WHITECROWPARROT_SWORD_PATH)
gamepad_buffer = GamepadBuffer()
player = Player(move_sheet=sheet, position=[80, 70], gamepad_buffer=gamepad_buffer)

done = False
while not done:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    done = joystick.get_button(7) == 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    player.gamepad_buffer.update(joystick)
    player.set_move()
    player.unhold_check()
    player.move_sheet.next_frame()

    screen.fill((0, 80, 180))
    screen.blit(player.move_sheet.current_image, player.position)
    clock.tick(30)
    pygame.display.flip()


pygame.quit()