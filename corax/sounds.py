from itertools import cycle

import corax.context as cctx
from corax.core import LOOP_TYPES, NODE_TYPES
from corax.euclide import Rect
from corax.iterators import shuffle
from corax.soundengine.io import (
    load_sound, play_sound, get_volume, set_volume, stop_sound)
from corax.seeker import find_element


LONG_SOUND_TYPES = NODE_TYPES.AMBIANCE, NODE_TYPES.MUSIC


def does_not_execute_on_muted(func):
    """
    Decorator to limit a function usage when the Corax context is muted
    """
    def wrapper(*args, **kwargs):
        if cctx.MUTE:
            return
        func(*args, **kwargs)
    return wrapper


class Ambiance():

    def __init__(self, filename, falloff, sound=None, zone=None, listener=None):
        self.filename = filename
        self.sound = sound or load_sound(filename)
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.listener = listener
        self.is_playing = False
        self._backed_volume = 1

    @does_not_execute_on_muted
    def play(self):
        play_sound(self.sound, loop=True)
        self.is_playing = True

    @does_not_execute_on_muted
    def pause(self):
        self._backed_volume = get_volume(self.sound)
        set_volume(self.sound, 0)

    @does_not_execute_on_muted
    def resume(self):
        set_volume(self.sound, self._backed_volume)

    @does_not_execute_on_muted
    def stop(self):
        stop_sound(self.sound)
        self.is_playing = False

    @does_not_execute_on_muted
    def evaluate(self):
        if self.zone is None or self.listener is None:
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
        set_volume(self.sound, ratio or 0)

    def __eq__(self, sound):
        message = "Ambiance only support comparison with str and Ambiance()"
        assert isinstance(sound, (str, Ambiance)), message
        if isinstance(sound, str):
            return sound == self.filename
        return sound.filename == self.filename


class SfxSoundCollection():

    def __init__(
            self,
            name,
            files,
            order,
            trigger,
            falloff,
            sounds=None,
            emitter=None,
            zone=None):

        self.name = name
        self.files = files
        self.sounds = sounds or [load_sound(f) for f in files]
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.emitter = emitter
        self.trigger = trigger
        if order == LOOP_TYPES.SHUFFLE:
            self.iterator = shuffle(self.sounds)
        else:
            self.iterator = cycle(self.sounds)

    @does_not_execute_on_muted
    def play(self):
        if not all((self.emitter, self.zone)):
            return
        position = self.emitter.pixel_center
        ratio = self.zone.falloff_ratio(position, self.falloff)
        sound = next(self.iterator)
        set_volume(sound, ratio or 0)
        play_sound(sound)

    @does_not_execute_on_muted
    def stop(self):
        for sound in self.sounds:
            stop_sound(sound)


class SfxSound():

    def __init__(
            self,
            name,
            filename,
            trigger,
            falloff=None,
            emitter=None,
            sound=None,
            zone=None):

        self.filename = filename
        self.sound = sound or load_sound(filename)
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.emitter = emitter
        self.trigger = trigger

    @does_not_execute_on_muted
    def play(self):
        if self.emitter and self.zone:
            position = self.emitter.pixel_center
            ratio = self.zone.falloff_ratio(position, self.falloff)
        else:
            ratio = 100
        set_volume(self.sound, ratio)
        play_sound(self.sound)

    @does_not_execute_on_muted
    def stop(self):
        stop_sound(self.sound)


class AudioStreamer():
    """
    This is the main class managing the sounds in memory, link them to they
    trigger and mix them togheter.
    """

    def __init__(self):
        self.sounds = []
        self.ambiances = []

    @does_not_execute_on_muted
    def shoot(self, triggers):
        if not any(triggers):
            return
        for trigger in triggers:
            for sound in self.sounds:
                if sound.trigger != trigger:
                    continue
                position = sound.emitter.pixel_center
                if sound.zone and sound.zone.contains(position) is False:
                    continue
                sound.play()

    def play_sound(self, filename):
        sound = load_sound(filename)
        print(sound)
        play_sound(sound)

    def pause(self):
        for sound in self.sounds:
            sound.stop()
        for sound in self.ambiances:
            sound.pause()

    def resume(self):
        for sound in self.ambiances:
            sound.resume()

    def stop(self):
        for sound in self.ambiances + self.sounds:
            sound.stop()

    def evaluate(self):
        for ambiance in self.ambiances:
            ambiance.evaluate()

    def set_scene(self, data, scene):
        loaded_sounds = list_loaded_sounds(self.sounds)
        new_ambiances, self.sounds = build_sound_scene(
            data=data,
            scene=scene,
            loaded_sounds=loaded_sounds,
            existing_ambiances=self.ambiances)
        for ambiance in self.ambiances:
            if ambiance not in new_ambiances:
                ambiance.stop()
        self.ambiances = new_ambiances


def build_sound_scene(data, scene, loaded_sounds, existing_ambiances):
    """
    This load the sound at scene switch.
    Sounds are heavy to keep in memory and lond to load. We can't keep them
    loaded in a persistant way. We analyse what sound object have to be kept
    from a scene to another, unload the unecessary anymore and load the not
    already loaded.
    """
    ambiances = []
    sounds = []
    for sound_data in data:
        if sound_data.get("type") in LONG_SOUND_TYPES:
            ambiance = build_ambiance(sound_data, existing_ambiances)
            element = find_element(scene, sound_data["listener"])
            ambiance.listener = element.coordinate
            ambiances.append(ambiance)
        elif sound_data.get("type") == NODE_TYPES.SFX:
            sound = SfxSound(
                name=sound_data["name"],
                filename=sound_data["file"],
                trigger=sound_data["trigger"],
                falloff=sound_data["falloff"],
                sound=loaded_sounds.get(sound_data.get("file")),
                zone=sound_data["zone"])
            element = find_element(scene, sound_data["emitter"])
            sound.emitter = element.coordinate
            sounds.append(sound)
        elif sound_data.get("type") == NODE_TYPES.SFX_COLLECTION:
            collection = build_sfx_collection(sound_data, loaded_sounds)
            element = find_element(scene, sound_data["emitter"])
            collection.emitter = element.coordinate
            sounds.append(collection)
    return ambiances, sounds


def build_sfx_collection(data, loaded_sounds):
    sounds = [
        loaded_sounds.get(f) if f in loaded_sounds else load_sound(f)
        for f in data["files"]]
    return SfxSoundCollection(
        name=data["name"],
        files=data["files"],
        order=data["order"],
        trigger=data["trigger"],
        falloff=data["falloff"],
        sounds=sounds,
        zone=data["zone"])


def list_loaded_sounds(sounds):
    """
    This function helps to recycle Sound object used in already loaded by the
    AudioStreamer. It receive a list of Corax sounds objects such as Ambiance,
    SfxSound, etc ... It convert all in dictionnary: {filename: Sound}.
    This is use when the AudioStreamer change scene. It allow to store those
    sounds and can be reassigned to the new scene if they are used again.
    """
    loaded = {}
    for sound in sounds:
        if isinstance(sound, SfxSoundCollection):
            for f, s in zip(sound.files, sound.sounds):
                loaded[f] = s
            continue
        loaded[sound.filename] = sound.sound
    return loaded


def find_matching_ambiance(filename, ambiances):
    for ambiance in ambiances:
        if ambiance == filename:
            return ambiance


def build_ambiance(data, ambiances=None):
    ambiances = ambiances or []
    matching = find_matching_ambiance(data.get("file"), ambiances)
    if not matching:
        return Ambiance(
            filename=data["file"],
            zone=data["zone"],
            falloff=data["falloff"])
    ambiance = Ambiance(
        filename=data["file"],
        zone=data["zone"],
        falloff=data["falloff"],
        sound=matching.sound)
    ambiance.is_playing = matching.is_playing
    return ambiance
