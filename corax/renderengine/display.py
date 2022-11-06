import moderngl
from moderngl_window import geometry, activate_context
import pygame
import corax.context as cctx
from corax.renderengine.io import get_shader
from corax.renderengine.window import Window


class CoraxWindow():

    def __init__(self, window):
        self.window = window
        self.ctx = window.ctx
        self.vsync = True
        self.screen = pygame.Surface(cctx.RESOLUTION, flags=pygame.SRCALPHA)
        self._textures = []
        self.time = 0
        self.frame = geometry.quad_fs()

    def textures(self):
        """
        To avoid recreating texture undefinitely, this generator only generate
        the necessary one onces and reuse existing.
        """
        i = 0
        while True:
            if i == len(self._textures):
                texture = self.ctx.texture(cctx.RESOLUTION, 4)
                texture.filter = moderngl.NEAREST, moderngl.NEAREST
                self._textures.append(texture)
            yield self._textures[i]
            i += 1

    def render(self, surfaces_and_shaders, events):
        self.window.clear(0, 0, 0, 0)
        self.window.use()
        self.ctx.clear()
        self.ctx.enable(moderngl.BLEND)
        textures = self.textures()
        for surface, shader in surfaces_and_shaders:
            texture = next(textures)
            texture.use()
            data = surface.get_view('2')
            texture.write(data)
            program = get_shader(
                shader, self.time, tuple(cctx.RESOLUTION), self.window.size)
            self.frame.render(program)
        self.ctx.disable(moderngl.BLEND)
        self.window.swap_buffers(events)
        self.time += 1

    @property
    def is_closing(self):
        return self.window.is_closing


def setup_render_display(scaled=True, fullscreen=True):
    # TODO: Implement scaled.

    window = Window(
        title=cctx.TITLE,
        size=cctx.RESOLUTION,
        fullscreen=fullscreen,
        resizable=False,
        gl_version=(3, 3),
        aspect_ratio=cctx.RESOLUTION[0] / cctx.RESOLUTION[1],
        vsync=True,
        samples=0,
        cursor=False)

    activate_context(window=window)
    window.swap_buffers([])
    return CoraxWindow(window=window)
