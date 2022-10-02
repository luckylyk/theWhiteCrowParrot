import moderngl
import moderngl_window
import pygame
from moderngl_window import geometry


class Window(moderngl_window.WindowConfig):
    title = "the White Crow Parrot"
    window_size = 800, 450

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = pygame.Surface(self.window_size, flags=pygame.SRCALPHA)

        self.layer_texture_1 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_1.filter = moderngl.NEAREST, moderngl.NEAREST
        self.layer_texture_2 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_2.filter = moderngl.NEAREST, moderngl.NEAREST
        self.layer_texture_3 = self.ctx.texture(self.window_size, 4)
        self.layer_texture_3.filter = moderngl.NEAREST, moderngl.NEAREST

        self.layer_program_1 = self.load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader1.glsl')
        self.layer_program_2 = self.load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader2.glsl')
        self.layer_program_3 = self.load_program('C:/perso/theWhiteCrowParrot/scripts/render_engine/shader3.glsl')

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

    def parse(self):
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

    def render(self, *args):
        self.ctx.clear()
        self.ctx.enable(moderngl.BLEND)
        for texture, surface, program, image in self.parse():
            surface.blit(image, (0, 0))
            texture.use()
            data = surface.get_view('1')
            texture.write(data)
            self.frame.render(program)
        self.ctx.disable(moderngl.BLEND)


from moderngl_window import (
    WindowConfig,
    setup_basic_logging,
    create_parser,
    parse_args,
    get_local_window_cls,
    activate_context,
    Timer,
    weakref,
    logger
)



def run_window_config_custom(config_cls: WindowConfig, timer=None, args=None) -> None:
    """
    Run an WindowConfig entering a blocking main loop

    Args:
        config_cls: The WindowConfig class to render
    Keyword Args:
        timer: A custom timer instance
        args: Override sys.args
    """
    setup_basic_logging(config_cls.log_level)
    parser = create_parser()
    config_cls.add_arguments(parser)
    values = parse_args(args=args, parser=parser)
    config_cls.argv = values
    window_cls = get_local_window_cls(values.window)

    # Calculate window size
    size = values.size or config_cls.window_size
    size = int(size[0] * values.size_mult), int(size[1] * values.size_mult)

    # Resolve cursor
    show_cursor = values.cursor
    if show_cursor is None:
        show_cursor = config_cls.cursor
    print(config_cls.gl_version)
    print(config_cls.aspect_ratio)
    print(config_cls.samples)
    window = window_cls(
        title=config_cls.title,
        size=size,
        fullscreen=config_cls.fullscreen or values.fullscreen,
        resizable=values.resizable
        if values.resizable is not None
        else config_cls.resizable,
        gl_version=config_cls.gl_version,
        aspect_ratio=config_cls.aspect_ratio,
        vsync=values.vsync if values.vsync is not None else config_cls.vsync,
        samples=values.samples if values.samples is not None else config_cls.samples,
        cursor=show_cursor if show_cursor is not None else True,
    )
    window.print_context_info()
    activate_context(window=window)
    timer = timer or Timer()
    config = config_cls(ctx=window.ctx, wnd=window, timer=timer)
    # Avoid the event assigning in the property setter for now
    # We want the even assigning to happen in WindowConfig.__init__
    # so users are free to assign them in their own __init__.
    window._config = weakref.ref(config)

    # Swap buffers once before staring the main loop.
    # This can trigged additional resize events reporting
    # a more accurate buffer size
    window.swap_buffers()
    window.set_default_viewport()

    timer.start()

    while not window.is_closing:
        current_time, delta = timer.next_frame()

        if config.clear_color is not None:
            window.clear(*config.clear_color)

        # Always bind the window framebuffer before calling render
        window.use()

        window.render(current_time, delta)
        if not window.is_closing:
            window.swap_buffers()

    _, duration = timer.stop()
    window.destroy()
    if duration > 0:
        logger.info(
            "Duration: {0:.2f}s @ {1:.2f} FPS".format(
                duration, window.frames / duration
            )
        )

if __name__ == '__main__':
    print(run_window_config_custom(Window, args=('--window', 'pygame2')))