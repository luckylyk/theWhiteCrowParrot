import pygame


class Joystick:
    """ Class to mock joystick using keyboard """

    def __init__(self):
        self.down = False
        self.up = False
        self.left = False
        self.right = False
        self.start = False
        self.select = False
        self.x = False
        self.y = False
        self.a = False
        self.b = False
        self.l1 = False
        self.l2 = False
        self.r1 = False
        self.r2 = False
        self.rsl = False
        self.rsr = False

    def init(self):
        pass

    def set_events(self, events):
        for event in events:
            if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
                continue
            match event.key:
                case pygame.K_ESCAPE:
                    self.start = event.type == pygame.KEYDOWN
                case pygame.K_F1:
                    self.select = event.type == pygame.KEYDOWN
                case pygame.K_UP:
                    self.up = event.type == pygame.KEYDOWN
                case pygame.K_DOWN:
                    self.down = event.type == pygame.KEYDOWN
                case pygame.K_LEFT:
                    self.left = event.type == pygame.KEYDOWN
                case pygame.K_RIGHT:
                    self.right = event.type == pygame.KEYDOWN
                case pygame.K_v:
                    self.r1 = event.type == pygame.KEYDOWN
                case pygame.K_b:
                    self.l1 = event.type == pygame.KEYDOWN
                case pygame.K_d:
                    self.r2 = event.type == pygame.KEYDOWN
                case pygame.K_f:
                    self.l2 = event.type == pygame.KEYDOWN
                case pygame.K_SPACE:
                    self.a = event.type == pygame.KEYDOWN
                case pygame.K_c:
                    self.x = event.type == pygame.KEYDOWN
                case pygame.K_x:
                    self.y = event.type == pygame.KEYDOWN
                case pygame.K_z:
                    self.b = event.type == pygame.KEYDOWN
                case pygame.K_a:
                    self.rsl = event.type == pygame.KEYDOWN
                case pygame.K_s:
                    self.rsr = event.type == pygame.KEYDOWN

    def get_button(self, button):
        match button:
            case 0:
                return int(self.a)
            case 1:
                return int(self.b)
            case 2:
                return int(self.x)
            case 3:
                return int(self.y)
            case 4:
                return int(self.l1)
            case 5:
                return int(self.r1)
            case 6:
                return int(self.select)
            case 7:
                return int(self.start)
        return 0

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
        match axis:
            case 0:
                return -1 if self.left else 1 if self.right else 0
            case 1:
                return -1 if self.up else 1 if self.down else 0
            case 2:
                return -1 if self.rsl else 1 if self.rsr else 0
            case 4:
                return int(self.l2)
            case 5:
                return int(self.r2)
