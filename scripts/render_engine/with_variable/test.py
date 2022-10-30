
import pygame
from pygame.locals import *

# pygame initialize
pygame.init()
clock = pygame.time.Clock()

# as usual you will create a display and give it a name
# i named my display as screen
# and you need to give it a Surface to replace old display
screen = pygame.Surface((800, 600)).convert((255, 65282, 16711681, 0))
# you need to give your display OPENGL flag to blit screen using OPENGL
pygame.display.set_mode((800, 600), pygame.DOUBLEBUF|pygame.OPENGL)
import moderngl

context = moderngl.create_context()
prog = context.program(
    vertex_shader=open(r"C:\perso\theWhiteCrowParrot\ModernGL-Shader-with-pygame\shaders\VERTEX_SHADER2.glsl").read(),
    fragment_shader=open(r"C:\perso\theWhiteCrowParrot\ModernGL-Shader-with-pygame\shaders\FRAGMENT_SHADER2.glsl").read(),
)