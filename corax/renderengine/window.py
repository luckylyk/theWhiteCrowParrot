from typing import Tuple
import pygame
import pygame.display
import pygame.event
import pygame._sdl2

from moderngl_window.context.base import BaseWindow
from moderngl_window.context.pygame2.keys import Keys


class Window(BaseWindow):
    """
    Basic window implementation using pygame2.
    """

    #: Name of the window
    name = "pygame2"
    #: pygame specific key constants
    keys = Keys

    _mouse_button_map = {
        1: 1,
        3: 2,
        2: 3,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        pygame.display.init()

        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MAJOR_VERSION, self.gl_version[0])
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_MINOR_VERSION, self.gl_version[1])
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

        if self.samples > 1:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, self.samples)

        self._depth = 24
        self._flags = pygame.OPENGL | pygame.DOUBLEBUF

        if self.resizable:
            self._flags |= pygame.RESIZABLE

        self._set_mode()
        self.title = self._title
        self.cursor = self._cursor
        # Get the reference for the internal sdl2 window
        # Makes us able to control window position and other properties.
        self._sdl_window = pygame._sdl2.video.Window.from_display_module()

        if self.fullscreen:
            self._set_fullscreen(True)

        self.init_mgl_context()
        self.set_default_viewport()

    def _set_mode(self):
        self._surface = pygame.display.set_mode(
            size=(self._width, self._height),
            flags=self._flags,
            depth=self._depth,
            vsync=self._vsync)

    def _set_fullscreen(self, value: bool) -> None:
        if value:
            self._sdl_window.set_fullscreen(True)
        else:
            self._sdl_window.set_windowed()

    def _set_vsync(self, value: bool) -> None:
        self._vsync = value
        self._set_mode()

    @property
    def size(self) -> Tuple[int, int]:
        """Tuple[int, int]: current window size.

        This property also support assignment::

            # Resize the window to 1000 x 1000
            window.size = 1000, 1000
        """
        return self._width, self._height

    @size.setter
    def size(self, value: Tuple[int, int]):
        self._width, self._height = value
        self._set_mode()
        self.resize(value[0], value[1])

    @property
    def position(self) -> Tuple[int, int]:
        """Tuple[int, int]: The current window position.

        This property can also be set to move the window::

            # Move window to 100, 100
            window.position = 100, 100
        """
        return self._sdl_window.position

    @position.setter
    def position(self, value: Tuple[int, int]):
        self._sdl_window.position = value

    @property
    def cursor(self) -> bool:
        """bool: Should the mouse cursor be visible inside the window?

        This property can also be assigned to::

            # Disable cursor
            window.cursor = False
        """
        return self._cursor

    @cursor.setter
    def cursor(self, value: bool):
        pygame.mouse.set_visible(value)
        self._cursor = value

    @property
    def mouse_exclusivity(self) -> bool:
        """bool: If mouse exclusivity is enabled.

        When you enable mouse-exclusive mode, the mouse cursor is no longer
        available. It is not merely hidden – no amount of mouse movement
        will make it leave your application. This is for example useful
        when you don't want the mouse leaving the screen when rotating
        a 3d scene.

        This property can also be set::

            window.mouse_exclusivity = True
        """
        return self._mouse_exclusivity

    @mouse_exclusivity.setter
    def mouse_exclusivity(self, value: bool):
        if self._cursor:
            self.cursor = False

        pygame.event.set_grab(value)
        self._mouse_exclusivity = value

    @property
    def title(self) -> str:
        """str: Window title.

        This property can also be set::

            window.title = "New Title"
        """
        return self._title

    @title.setter
    def title(self, value: str):
        pygame.display.set_caption(value)
        self._title = value

    def swap_buffers(self, events) -> None:
        """
        Swap buffers, set viewport, trigger events and increment frame counter
        """
        pygame.display.flip()
        self.set_default_viewport()

        for event in events:
            if event.type == pygame.VIDEORESIZE:
                self.resize(event.size[0], event.size[1])

        self._frames += 1

    def _set_icon(self, icon_path: str) -> None:
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)

    def resize(self, width, height) -> None:
        """Resize callback

        Args:
            width: New window width
            height: New window height
        """
        self._width = width
        self._height = height
        self._buffer_width, self._buffer_height = self._width, self._height
        self.set_default_viewport()

        super().resize(self._buffer_width, self._buffer_height)
