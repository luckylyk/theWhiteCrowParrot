from moderngl_window.context.pygame2 import Window
import pygame
import moderngl
from moderngl_window import geometry
from moderngl_window.meta import ProgramDescription
from moderngl_window import resources


def load_program(
        path=None,
        vertex_shader=None,
        geometry_shader=None,
        fragment_shader=None,
        tess_control_shader=None,
        tess_evaluation_shader=None,
        defines=None,
        varyings=None):

    return resources.programs.load(
        ProgramDescription(
            path=path,
            vertex_shader=vertex_shader,
            geometry_shader=geometry_shader,
            fragment_shader=fragment_shader,
            tess_control_shader=tess_control_shader,
            tess_evaluation_shader=tess_evaluation_shader,
            defines=defines,
            varyings=varyings,
        )
    )


class CoraxWindow(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        activate_context(self)
        self.clear_color = (0.0, 0.0, 0.0, 0.0)
        self.window_size = kwargs['size']
        self.screen = pygame.Surface(self.window_size, flags=pygame.SRCALPHA)

        self.layer_texture_1 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_1.filter = moderngl.NEAREST, moderngl.NEAREST
        self.layer_texture_2 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_2.filter = moderngl.NEAREST, moderngl.NEAREST
        self.layer_texture_3 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_3.filter = moderngl.NEAREST, moderngl.NEAREST

        self.layer_surface_1 = pygame.Surface(self.window_size, flags=pygame.SRCALPHA)
        self.layer_surface_2 = pygame.Surface(self.window_size, flags=pygame.SRCALPHA)
        self.layer_surface_3 = pygame.Surface(self.window_size, flags=pygame.SRCALPHA)

        self.image_1 = pygame.image.load('C:/perso/theWhiteCrowParrot/scripts/render_engine/bg.png').convert()
        self.image_2 = pygame.image.load('C:/perso/theWhiteCrowParrot/scripts/render_engine/mg.png').convert()
        self.image_3 = pygame.image.load('C:/perso/theWhiteCrowParrot/scripts/render_engine/fg.png').convert()
        self.image_1.set_colorkey([0, 255, 0])
        self.image_2.set_colorkey([0, 255, 0])
        self.image_3.set_colorkey([0, 255, 0])

        self.frame = geometry.quad_fs()

    def load_shaders(self):

        self.layer_program_1 = load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader1.glsl')
        self.layer_program_2 = load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader2.glsl')
        self.layer_program_3 = load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader3.glsl')

    def iter(self):
        textures = (
            self.layer_texture_1,
            self.layer_texture_2,
            self.layer_texture_3)
        surfaces = (
            self.layer_surface_1,
            self.layer_surface_2,
            self.layer_surface_3)
        programs = (
            self.layer_program_1,
            self.layer_program_2,
            self.layer_program_3)
        images = (
            self.image_1,
            self.image_2,
            self.image_3)
        yield from zip(textures, surfaces, programs, images)

    def render(self, *args, **kwargs):
        super().render(*args, **kwargs)
        self.ctx.clear()
        self.ctx.enable(moderngl.BLEND)
        for texture, surface, program, image in self.iter():
            print(texture, surface, program, image)
            surface.blit(image, (0, 0))
            texture.use()
            data = surface.get_view('1')
            texture.write(data)
            self.frame.render(program)
        self.ctx.disable(moderngl.BLEND)


from moderngl_window import activate_context
window = CoraxWindow(
    title="the White Crow Parrot",
    size=(800, 450),
    fullscreen=False,
    resizable=False,
    gl_version=(3, 3),
    aspect_ratio=1.7777777777777777,
    vsync=True,
    samples=0,
    cursor=False,
)
window.load_shaders()
window.swap_buffers()
window.set_default_viewport()
import pygame


timer = pygame.time.Clock()

while not window.is_closing:
    window.use()
    window.render(1, 1)
    timer.tick(30)
    continue