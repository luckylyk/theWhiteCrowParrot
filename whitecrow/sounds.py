from whitecrow.loaders import load_sound
from whitecrow.euclide import Rect
import pygame


class Ambiance():
    def __init__(self, filename, zone, falloff, channel, listener=None):
        self.channel = channel
        self.voice = pygame.mixer.Channel(channel)
        self.sound = load_sound(filename)
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.listener = listener
        self.is_playing = False

    def play(self):
        self.sound.play(-1)
        self.is_playing = True

    def stop(self):
        self.sound.stop()
        self.is_playing = False

    def update(self):
        if self.zone is None:
            if self.is_playing is False:
                self.play()
            return
        position = self.listener.pixel_center
        if self.is_playing is False:
            if self.zone.contains(position):
                self.play()
                return
        elif self.zone.contains(position) is False:
            self.stop()
            return
        ratio = self.zone.falloff_ratio(position, self.falloff)
        self.sound.set_volume(ratio)