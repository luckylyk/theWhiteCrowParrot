import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

# Initialisation de pygame et de la fenêtre
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)

# Définition d'un simple shader GLSL
vertex_shader = """
#version 330 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec2 texCoord;
out vec2 fragTexCoord;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    fragTexCoord = texCoord;
}
"""

fragment_shader = """
#version 330 core
in vec2 fragTexCoord;
out vec4 color;
uniform sampler2D textureSampler;
void main() {
    color = texture(textureSampler, fragTexCoord);
}
"""

def apply_shader(surface):
    # Convertir la surface en texture OpenGL
    surface_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, surface_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Création du programme de shader
    shader_program = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    )

    glUseProgram(shader_program)

    # Application du shader sur la texture (dans ce cas, nous utilisons une texture simple)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Configurer la géométrie pour le rendu (ici un simple rectangle couvrant toute la surface)
    vertices = [
        -1.0, -1.0, 0.0, 0.0,
         1.0, -1.0, 1.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
        -1.0,  1.0, 0.0, 1.0
    ]
    vertices = numpy.array(vertices, dtype=numpy.float32)

    # Création d'un VBO et d'un VAO pour dessiner la texture sur le rectangle
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    glVertexAttribPointer(0, 2, GL_FLOAT, False, 4 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, False, 4 * 4, ctypes.c_void_p(2 * 4))
    glEnableVertexAttribArray(1)

    # Dessiner la surface appliquée au shader
    glDrawArrays(GL_QUADS, 0, 4)

    # Désactivation des objets et du shader
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    glUseProgram(0)

    # Libérer les ressources
    glDeleteTextures(1, [texture_id])
    glDeleteBuffers(1, [vbo])
    glDeleteVertexArrays(1, [vao])

# Appliquez votre shader sur une surface pygame
surface = pygame.Surface((400, 300))
surface.fill((255, 0, 0))  # Remplir la surface avec une couleur rouge

# Appliquer le shader avant de mettre à l'échelle
apply_shader(surface)

# Mettre à l'échelle la surface après application du shader
scaled_surface = pygame.transform.scale(surface, (800, 600))

# Afficher l'image mise à l'échelle
screen.blit(scaled_surface, (0, 0))
pygame.display.flip()

# Boucle d'événements pour afficher la fenêtre
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
