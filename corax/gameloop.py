import copy
import logging
import os
import pickle
import pygame

import corax.context as cctx
from corax.core import RUN_MODES, MENU_EVENTS, GAMELOOP_ACTIONS
from corax.gamepad import is_joystick_connected
from corax.iterators import fade
from corax.menu import Menu
from corax.override import load_json
from corax.pygameutils import escape_in_events, tab_in_events, space_in_events
from corax.theatre import Theatre


class GameLoop:
    def __init__(self, data):
        self.data = data
        self.done = False
        self.clock = pygame.time.Clock()
        # This is a mode forcing the game to be evaluation frame per frame.
        self.frame_per_frame_mode = False
        # Theatre is the main controller class. It drive the story, build and
        # load the scenes.
        self.theatre = Theatre(copy.deepcopy(self.data))
        self.checkpoint = None
        self.has_connected_joystick = False
        self.joystick = pygame.joystick.Joystick(0)
        filename = os.path.join(cctx.MENU_FOLDER, data["menu"])
        self.menu = Menu(load_json(filename))

    def __next__(self, events):
        self.done = escape_in_events(events)
        if self.done:
            return

        if tab_in_events(events):
            self.frame_per_frame_mode = not self.frame_per_frame_mode

        if self.frame_per_frame_mode and not space_in_events(events):
            return

        self.joystick.init()
        self.has_connected_joystick = is_joystick_connected()
        if not self.has_connected_joystick:
            return

        self.menu.evaluate(self.joystick)
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
            self.clock.tick(cctx.FPS)
            return

        self.evaluate_theatre()
        fps = self.clock.get_fps()
        if int(fps) > cctx.FPS:
            logging.debug(f"FPS DROP DOWN -> {fps}")
        self.clock.tick(cctx.FPS)

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

        self.theatre.evaluate(self.joystick)

    def save_checkpoint(self):
        self.theatre.checkpoint_requested = False
        self.checkpoint = pickle.dumps(self.theatre)
        logging.debug('Checkpoint saved.')
