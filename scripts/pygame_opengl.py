
import numpy
from ctypes import c_uint

from OpenGL.GL import *

from OpenGL.GL.shaders import compileShader
from OpenGL.GL.EXT.framebuffer_object import (
    glBindFramebufferEXT,
    GL_FRAMEBUFFER_EXT,
    glFramebufferTexture2DEXT,
    GL_COLOR_ATTACHMENT0_EXT)
import pygame


UNIFORM_TEX = 0
UNIFORM_FLOAT = 1
UNIFORM_VEC2 = 2
UNIFORM_VEC3 = 3
UNIFORM_VEC4 = 4
UNIFORM_INT = 5

GL_TEXTURES = [
    GL_TEXTURE0,
    GL_TEXTURE1,
    GL_TEXTURE2,
    GL_TEXTURE3,
    GL_TEXTURE4,
    GL_TEXTURE5,
    GL_TEXTURE6,
    GL_TEXTURE7,
    GL_TEXTURE8,
    GL_TEXTURE9,
    GL_TEXTURE10,
    GL_TEXTURE11]

UNIFORM_MAP = {
    UNIFORM_TEX: glUniform1i,
    UNIFORM_FLOAT: glUniform1f,
    UNIFORM_INT: glUniform1i,
    UNIFORM_VEC2: glUniform2f,
    UNIFORM_VEC3: glUniform3f,
    UNIFORM_VEC4: glUniform4f,
}

TEXT_COORDS = [
    0.0, 1.0,
    0.0, 0.0,
    1.0, 0.0,
    1.0, 1.0
]

BASE_VERTICES = [
    -1.0, 1.0,
    -1.0, -1.0,
    1.0, -1.0,
    1.0, 1.0,
]


def read_f(path):
    with open(path, 'r') as f:
        data = f.read()
    return data


def shade_surf(surf, shader, config=None):
    config = config or {}
    tex = WrappedTexture(surf)
    tex.set_shader(shader)
    surf = tex.to_surf(config=config)
    tex.delete()
    return surf


class PygameOpenGLWin:
    def __init__(self, dimensions, caption='Pygame OpenGL'):
        self.dimensions = dimensions

        pygame.init()
        flags = pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF
        pygame.display.set_mode(tuple(dimensions), flags)
        pygame.display.set_caption(caption)

        glViewport(0, 0, *dimensions)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.screen = pygame.Surface(dimensions, pygame.SRCALPHA)
        self.base_vertices = numpy.array(BASE_VERTICES, dtype=numpy.float32)
        self.texcoords = numpy.array(TEXT_COORDS, dtype=numpy.float32)

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, self.base_vertices)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, self.texcoords)

        self.fg_queue = []

    def render_bg(self, wtex, pos, config=None):
        wtex.draw(pos, config=config or {})

    def render_fg(self, wtex, pos, config=None):
        self.fg_queue.append((wtex, pos, config or {}))

    def update_clear(self, color=(0, 0, 0), config=None, shader=None):
        screen_tex = WrappedTexture(self.screen, self)
        if shader:
            screen_tex.set_shader(shader)
        screen_tex.draw((0, 0), config=config or {})

        for task in self.fg_queue:
            task[0].draw(task[1], config=task[2])

        screen_tex.delete()
        self.fg_queue = []

        pygame.display.flip()
        alpha = color[3] / 255 if len(color) > 3 else 1
        glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, alpha)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def clear(self, color=(0, 0, 0)):
        pygame.display.flip()
        alpha = color[3] / 255 if len(color) > 3 else 1
        glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, alpha)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class Uniform:
    def __init__(self, shader_obj, name, datatype):
        self.shader_obj = shader_obj
        self.datatype = datatype
        self.name = name
        self.uniform = glGetUniformLocation(shader_obj.program, name)

        self.tex_id = -1
        if datatype == UNIFORM_TEX:
            self.tex_id = shader_obj.tex_ids[name]

    def apply(self, value):
        if self.datatype == UNIFORM_TEX:
            UNIFORM_MAP[self.datatype](self.uniform, self.tex_id)
            glActiveTexture(GL_TEXTURES[self.tex_id])
            value.set()
        elif self.datatype in [UNIFORM_VEC2, UNIFORM_VEC3, UNIFORM_VEC4]:
            UNIFORM_MAP[self.datatype](self.uniform, *value)
        else:
            UNIFORM_MAP[self.datatype](self.uniform, value)


class Shader:
    def __init__(self, frag_shader, vert_shader=None):
        self.frag_path = frag_shader + '.frag'
        self.vert_path = (vert_shader or frag_shader) + '.vert'
        data = read_f(self.vert_path)
        self.vert_shader = compileShader(data, GL_VERTEX_SHADER)
        data = read_f(self.frag_path)
        self.frag_shader = compileShader(data, GL_FRAGMENT_SHADER)
        self.program = glCreateProgram()
        glAttachShader(self.program, self.vert_shader)
        glAttachShader(self.program, self.frag_shader)
        glLinkProgram(self.program)
        self.uniforms = []
        self.tex_ids = {}
        self.next_tex_id = 0
        self.primary_tex = None
        self.rect_uniform = Uniform(self, 'rectVec', UNIFORM_VEC4)
        self.rect = 0.0, 0.0, 1.0, 1.0

    def add_uniform(self, uniform_name, datatype):
        if datatype == UNIFORM_TEX:
            if not self.primary_tex:
                self.primary_tex = uniform_name

            self.tex_ids[uniform_name] = self.next_tex_id
            self.next_tex_id += 1

        self.uniforms.append(Uniform(self, uniform_name, datatype))

    def add_uniforms(self, uniform_map):
        for uniform in uniform_map:
            self.add_uniform(uniform, uniform_map[uniform])

    def apply_rect(self, vec4):
        self.rect = vec4

    def apply(self, config):
        glUseProgram(self.program)
        self.rect_uniform.apply(self.rect)
        for uniform in self.uniforms:
            if uniform.name in config:
                uniform.apply(config[uniform.name])


class Texture:
    def __init__(self, src):
        self.img = pygame.image.load(src) if isinstance(src, str) else src

        self.tex_data = pygame.image.tostring(self.img, 'RGBA', 1)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        # GL_LINEAR_MIPMAP_LINEAR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, self.tex_data)

    def set(self):
        glBindTexture(GL_TEXTURE_2D, self.tex_id)

    def delete(self):
        glDeleteTextures(1, [self.tex_id])


class WrappedTexture:
    def __init__(self, src, window=None):
        self.texture = Texture(src)
        self.window = window
        self.wdimensions = window.dimensions if window else self.texture.img.get_size()
        self.scale = [
            self.texture.width / self.wdimensions[0],
            self.texture.height / self.wdimensions[1]]
        self.shader = None

    def set_shader(self, shader):
        self.shader = shader

    def draw(self, pos, config=None):
        config = config or {}
        vec_rect = (
            pos[0] / self.wdimensions[0] * 2,
            pos[1] / self.wdimensions[1] * 2,
            self.scale[0],
            self.scale[1])

        if self.shader:
            self.shader.apply_rect(vec_rect)
            if self.shader.primary_tex:
                config[self.shader.primary_tex] = self.texture
            self.shader.apply(config)

        glDrawArrays(GL_QUADS, 0, 4)  # the 4 is the vertex count

    def to_surf(self, config=None):
        config = config or {}
        # generate target texture and parameters
        render_target = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, render_target)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, self.texture.width, self.texture.height,
            0, GL_RGBA, GL_UNSIGNED_INT, None)

        # generate framebuffer
        fbo = c_uint(1)
        glGenFramebuffers(1, fbo)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo)
        glFramebufferTexture2DEXT(
            GL_FRAMEBUFFER_EXT,
            GL_COLOR_ATTACHMENT0_EXT,
            GL_TEXTURE_2D,
            render_target, 0)
        glPushAttrib(GL_VIEWPORT_BIT)

        glViewport(0, 0, self.texture.width, self.texture.height)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.draw((0, 0), config=config)

        # switch back to normal rendering
        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        glBindTexture(GL_TEXTURE_2D, render_target)
        raw_tex_data = glGetTexImage(
            GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        size = self.texture.width, self.texture.height
        pg_surf = pygame.image.fromstring(raw_tex_data, size, 'RGBA', True)

        glDeleteTextures(1, [render_target])
        # glDeleteFramebuffers(1)

        return pg_surf

    def delete(self):
        self.texture.delete()


def escape_in_events(events):
    return any(
        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or
        event.type == pygame.QUIT
        for event in events)


clock = pygame.time.Clock()
wind = PygameOpenGLWin((500, 500))
text = WrappedTexture('C:/perso/theWhiteCrowParrot/whitecrowparrot/sets/airlock/bg.png', wind)

while 1:
    events = pygame.event.get()
    if escape_in_events(events):
        break
    print(text.to_surf())
    wind.clear(color=(.5, .5, .5))
    clock.tick(25)
