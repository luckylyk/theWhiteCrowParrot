from itertools import cycle

from whitecrow.loaders import load_sound
from whitecrow.euclide import Rect
from whitecrow.iterators import shuffle
from whitecrow.core import LOOP_TYPES

import pygame


class Ambiance():
    def __init__(self, filename, falloff, zone=None, listener=None):
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


class SfxSoundCollection():
    def __init__(
            self,
            name,
            files,
            order,
            trigger,
            falloff,
            emitter=None,
            zone=None):

        self.sounds = [load_sound(f) for f in files]
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.emitter = emitter
        self.trigger = trigger
        if order == LOOP_TYPES.SHUFFLE:
            self.iterator = shuffle(self.sounds)
        else:
            self.iterator = cycle(self.sounds)

    def play(self):
        position = self.emitter.pixel_center
        ratio = self.zone.falloff_ratio(position, self.falloff)
        sound = next(self.iterator)
        sound.set_volume(ratio)
        sound.play()


class SfxSound():
    def __init__(
            self,
            name,
            filename,
            trigger,
            falloff,
            emitter=None,
            zone=None):

        self.sound = load_sound(filename)
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.emitter = emitter
        self.trigger = trigger

    def play(self):
        position = self.emitter.pixel_center
        ratio = self.zone.falloff_ratio(position, self.falloff)
        self.sound.set_volume(ratio)
        self.sound.play()


class SoundShooter():
    def __init__(self):
        self.sounds = []
        self.triggers = []

    def shoot(self):
        for trigger in self.triggers:
            for sound in self.sounds:
                print(trigger, sound.trigger, self.triggers)
                if sound.trigger != trigger:
                    continue
                position = sound.emitter.pixel_center
                if sound.zone and sound.zone.contains(position) is False:
                    continue
                sound.play()
        self.triggers = []