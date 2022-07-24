import copy
import logging
import os
import pickle
import pygame

import corax.context as cctx
from corax.core import RUN_MODES, MENU_EVENTS, GAMELOOP_ACTIONS, COLORS
from corax.iterators import fade
from corax.menu import Menu
from corax.override import load_json
from corax.pygameutils import render_centered_text, escape_in_events
from corax.theatre import Theatre


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
        events = pygame.event.get()
        self.done = escape_in_events(events)
        if self.done:
            return
        self.joystick.init()

        self.menu.evaluate(self.screen, self.joystick)
        event = self.menu.collect_event()
        if event == MENU_EVENTS.ENTER:
            self.theatre.pause()
        elif event in [MENU_EVENTS.QUIT, GAMELOOP_ACTIONS.RESUME]:
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
            events = pygame.event.get()
            if escape_in_events(events):
                pygame.quit()

    def evaluate_theatre(self):
        if self.theatre.checkpoint_requested is True:
            self.save_checkpoint()

        if self.theatre.run_mode == RUN_MODES.RESTORE:
            self.theatre.audio_streamer.stop()
            self.theatre.run_mode = RUN_MODES.NORMAL
            if self.checkpoint is None:
                self.theatre = Theatre(copy.deepcopy(self.data))
                logging.debug('No checkpoint found, gamerestart.')
            else:
                self.theatre = pickle.loads(self.checkpoint)
                # TODO: move the magic number '50' as an option of restore
                # function : "restore 50"
                trans = fade(50, maximum=255, reverse=True)
                self.theatre.transition = trans
                self.theatre.alpha = 0
                logging.debug('Checkpoint loaded.')

        elif self.theatre.run_mode == RUN_MODES.RESTART:
            self.theatre.audio_streamer.stop()
            self.theatre = Theatre(copy.deepcopy(self.data))
            logging.debug('Game restart.')

        self.theatre.evaluate(self.joystick, self.screen)

    def save_checkpoint(self):
        self.theatre.checkpoint_requested = False
        self.checkpoint = pickle.dumps(self.theatre)
        logging.debug('Checkpoint saved.')
