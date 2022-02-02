import pygame
import corax.context as cctx


class Joystick:
    """ Class to mock joystick using keyboard """

    def __init__(self):
        self.down = False
        self.up = False
        self.left = False
        self.right = False
        self.start= False
        self.x = False
        self.y = False
        self.r2 = False

    def init(self):
        pass

    def set_events(self, events):
        for event in events:
            if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
                continue
            if event.key == pygame.K_SPACE:
                self.r2 = event.type == pygame.KEYDOWN
            if event.key == pygame.K_x:
                self.y = event.type == pygame.KEYDOWN
            if event.key == pygame.K_c:
                self.x = event.type == pygame.KEYDOWN
            start_keys = [pygame.K_KP_ENTER, pygame.KSCAN_KP_ENTER, pygame.K_RETURN, pygame.K_ESCAPE]
            if event.key in start_keys:
               self.start = event.type == pygame.KEYDOWN
            if event.key == pygame.K_UP:
               self.up = event.type == pygame.KEYDOWN
            if event.key == pygame.K_DOWN:
                self.down = event.type == pygame.KEYDOWN
            if event.key == pygame.K_LEFT:
                self.left = event.type == pygame.KEYDOWN
            if event.key == pygame.K_RIGHT:
                self.right = event.type == pygame.KEYDOWN

    def get_button(self, button):
        if button not in [2, 3, 7]:
            return 0
        elif button == 2:
            return int(self.x)
        elif button == 3:
            return int(self.y)
        elif button == 7:
            return int(self.start)

    def get_hat(self, *_):
        hat = [0, 0]
        if self.left:
            hat[0] = -1
        elif self.right:
            hat[0] = 1
        if self.up:
            hat[1] = 1
        elif self.down:
            hat[1] = -1
        return hat

    def get_axis(self, axis):
        if axis != 5 or not self.r2:
            return 0
        return 1
