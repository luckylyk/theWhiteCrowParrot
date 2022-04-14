
from corax.core import MENU_MODES, MENU_EVENTS
from corax.gamepad import InputBuffer
from corax.pygameutils import (
    load_sound, render_text, render_background, play_sound)
from corax.screen import screen_relative_y


class Menu:
    def __init__(self, data):
        self.data = data
        self.done = True
        self.event = None
        self.input_buffer = InputBuffer()
        self.sounds = {k: load_sound(v) for k, v in data["sounds"].items()}
        self.items = self.build_items()
        self.index = 0
        self.animation = None

    def build_items(self):
        x = 0 - self.data["left"] - self.data["column_width"]
        t, l = self.data["top"], self.data["left"]
        return [
            MenuItem(
                text=item["text"],
                event=item["event"],
                origin=[x, t + (self.data["row_height"] * i)],
                destination=[l, t + (self.data["row_height"] * i)],
                speed=self.data["speed"],
                acceleration=self.data["acceleration"])
            for i, item in enumerate(self.data["content"])]

    def collect_event(self):
        result = self.event
        self.event = None
        return result

    def set_next(self):
        play_sound(self.sounds["next"])
        self.index += 1
        if self.index == len(self.items):
            self.index = 0

    def set_previous(self):
        play_sound(self.sounds["previous"])
        if self.index == 0:
            self.index = len(self.items) - 1
            return
        self.index -= 1

    def trigger(self):
        play_sound(self.sounds["press"])
        return self.data["content"][self.index].get("event")

    def enter(self):
        self.done = False
        play_sound(self.sounds["enter"])
        self.animation = self.enter_animation()
        self.index = 0

    def quit(self, event=None):
        play_sound(self.sounds["quit"])
        event = event or MENU_EVENTS.QUIT
        self.animation = self.leave_animation(event)

    def evaluate(self, screen, joystick):
        if self.animation is not None:
            try:
                next(self.animation)
            except StopIteration:
                self.animation = None

        keypressed = self.input_buffer.update(joystick)
        if not keypressed:
            if self.mode != MENU_MODES.INACTIVE:
                self.render(screen)
            return

        buttons = self.input_buffer.pressed_delta()
        if self.mode == MENU_MODES.INACTIVE:
            if "start" in buttons:
                self.enter()
            return
        elif "DOWN" in buttons:
            self.set_next()
        elif "UP" in buttons:
            self.set_previous()
        elif "B" in buttons:
            self.quit()
        elif "A" in buttons or "X" in buttons or "start" in buttons:
            self.quit(self.data["content"][self.index].get("event"))
        self.render(screen)

    def enter_animation(self):
        self.event = MENU_EVENTS.ENTER
        self.done = False
        for item in self.items:
            item.enter()
            for _ in range(self.data["overlap"]):
                for item in self.items:
                    item.evaluate()
                yield
        while any(item.mode != MENU_MODES.INTERACTIVE for item in self.items):
            for item in self.items:
                item.evaluate()
            yield

    def leave_animation(self, event):
        for item in self.items:
            item.leave()
            for _ in range(self.data["overlap"]):
                for item in self.items:
                    item.evaluate()
                yield
        while any(item.mode != MENU_MODES.INACTIVE for item in self.items):
            for item in self.items:
                item.evaluate()
            yield
        self.done = True
        self.event = event

    def render(self, screen):
        render_background(
            screen,
            self.data["background_color"],
            self.data["background_alpha"])

        for i, item in enumerate(self.items):
            key = "text_color" if i != self.index else "current_text_color"
            render_text(
                screen=screen,
                color=self.data[key],
                x=item.position[0],
                y=item.position[1],
                text=item.text,
                bold=(i == self.index),
                size=self.data["size"])

    @property
    def mode(self):
        if all(item.mode == MENU_MODES.INTERACTIVE for item in self.items):
            return MENU_MODES.INTERACTIVE
        elif all(item.mode == MENU_MODES.INACTIVE for item in self.items):
            return MENU_MODES.INACTIVE
        return MENU_MODES.ANIMATED


class MenuItem:
    def __init__(self, text, event, origin, destination, speed, acceleration):
        self.acceleration = acceleration
        self.destination = [destination[0], screen_relative_y(destination[1])]
        self.event = event
        self.origin = [origin[0], screen_relative_y(origin[1])]
        self.position = self.origin[:]
        self.speed = speed
        self.text = text
        self.animation = None

    def evaluate(self):
        if self.animation is not None:
            try:
                next(self.animation)
            except StopIteration:
                self.animation = None

    @property
    def mode(self):
        if self.animation is not None:
            return MENU_MODES.ANIMATED
        elif self.position == self.origin:
            return MENU_MODES.INACTIVE
        if self.position == self.destination:
            return MENU_MODES.INTERACTIVE
        return MENU_MODES.INACTIVE

    def leave(self):
        self.animation = self.leave_animation()

    def enter(self):
        self.animation = self.enter_animation()

    def enter_animation(self):
        speed = self.speed
        while True:
            speed *= self.acceleration
            self.position[0] += speed
            if self.position[0] > self.destination[0]:
                self.position[0] = self.destination[0]
                break
            yield

    def leave_animation(self):
        speed = self.speed
        while True:
            speed *= self.acceleration
            self.position[0] -= speed
            if self.position[0] < self.origin[0]:
                self.position[0] = self.origin[0]
                break
            yield

