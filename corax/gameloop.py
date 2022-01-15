
import copy
import os
import pygame

import corax.context as cctx
from corax.core import RUN_MODES, MENU_EVENTS, GAMELOOP_ACTIONS, COLORS
from corax.theatre import Theatre
from corax.menu import Menu
from corax.override import load_json
from corax.pygameutils import render_centered_text, escape_in_events, draw_letterbox


CONNECT_CONTROLLER_WARNING = "Connect game controller (X Input)"


class GameLoop:
    def __init__(self, data, screen):
        self.data = data
        self.done = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        # Theatre is the main controller class. It drive the story, build and
        # load the scenes.
        self.theatre = Theatre(copy.deepcopy(self.data))
        self.checkpoint = None
        self.ensure_controller_connected()
        self.joystick = pygame.joystick.Joystick(0)
        filename = os.path.join(cctx.MENU_FOLDER, data["menu"])
        self.menu = Menu(load_json(filename))

    def __next__(self):
        self.ensure_controller_connected()
        self.joystick.init()
        events = pygame.event.get()
        self.done = escape_in_events(events)
        if self.done:
            return

        self.menu.evaluate(self.screen, self.joystick)
        event = self.menu.collect_event()
        if event == MENU_EVENTS.ENTER:
            self.theatre.pause()
        elif event in [MENU_EVENTS.QUIT,  GAMELOOP_ACTIONS.RESUME]:
            self.theatre.resume()
        elif event == GAMELOOP_ACTIONS.EXIT:
            self.done = True
        elif event == GAMELOOP_ACTIONS.RESTART:
            self.theatre.run_mode = RUN_MODES.RESTART

        if not self.menu.done:
            pygame.display.flip()
            self.theatre.render(self.screen)
            self.clock.tick(cctx.FPS)
            return

        self.evaluate_theatre()
        pygame.display.flip()
        self.clock.tick(cctx.FPS)

    def ensure_controller_connected(self):
        while pygame.joystick.get_count() == 0:
            pygame.joystick.quit()
            pygame.joystick.init()

            render_centered_text(
                self.screen,
                CONNECT_CONTROLLER_WARNING,
                COLORS.WHITE)

            pygame.display.flip()
            self.clock.tick(cctx.FPS)

    def evaluate_theatre(self):
        if self.theatre.run_mode == RUN_MODES.RESTART:
            self.theatre.audio_streamer.stop()
            self.theatre = Theatre(copy.deepcopy(self.data))
        self.theatre.evaluate(self.joystick, self.screen)
