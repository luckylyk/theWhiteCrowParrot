import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


import json
import pygame
from whitecrow.options import OPTIONS, ANIMATION_FOLDER
from whitecrow.animation import AnimationSheet
from whitecrow.graphicutils import load_images
from whitecrow.character import Player

WHITECROWPARROT_SWORD_PATH = os.path.join(ANIMATION_FOLDER, "whitecrowparrot_sword.json")
with open(WHITECROWPARROT_SWORD_PATH) as f:
    WHITECROWPARROT_SWORD_DATA = json.load(f)
k=0
pygame.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
screen = pygame.display.set_mode(OPTIONS["resolution"], pygame.FULLSCREEN)
pygame.display.set_caption("the White Crow Parrot")
clock = pygame.time.Clock()
done = False
filename = WHITECROWPARROT_SWORD_DATA["filename"]
block_size = WHITECROWPARROT_SWORD_DATA["block_size"]
key_color = WHITECROWPARROT_SWORD_DATA["key_color"]
images = load_images(filename, block_size, key_color)
sheet = AnimationSheet(WHITECROWPARROT_SWORD_DATA, images)
player = Player(animationsheet=sheet, position=[80, 70])


while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    if joystick.get_button(7) == 1:
        done = True

    player.set_joystick(joystick) == 1
    player.set_animation()
    player.unhold_check()
    player.animationsheet.next_frame()

    screen.fill((0, 80, 180))
    screen.blit(player.animationsheet.current_image, player.position)
    clock.tick(30)
    pygame.display.flip()



pygame.quit()