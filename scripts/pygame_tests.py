import pygame
from pygame.locals import *

pygame.init()

RES=(160, 120)
FPS=30
clock = pygame.time.Clock()
screen = pygame.display.set_mode(RES, DOUBLEBUF)

done=False

while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True

    screen.fill((255,0,255))
    pygame.draw.circle(screen, (0,0,0), (100,100), 20)
    pygame.draw.circle(screen, (0,0,200), (0,0), 10)
    pygame.draw.circle(screen, (200,0,0), (160,120), 30)
    pygame.draw.line(screen, (250,250,0), (0,120), (160,0))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()