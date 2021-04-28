from itertools import cycle

import corax.context as cctx
from corax.core import LOOP_TYPES, NODE_TYPES
from corax.pygameutils import load_sound
from corax.euclide import Rect
from corax.iterators import shuffle
from corax.seeker import find_element


LONG_SOUND_TYPES = NODE_TYPES.AMBIANCE, NODE_TYPES.MUSIC


def not_executed_when_muted(func):
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

    @not_executed_when_muted
    def play(self):
        self.sound.play(-1)
        self.is_playing = True

    @not_executed_when_muted
    def stop(self):
        self.sound.stop()
        self.is_playing = False

    @not_executed_when_muted
    def evaluate(self):
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

    @not_executed_when_muted
    def play(self):
        position = self.emitter.pixel_center
        ratio = self.zone.falloff_ratio(position, self.falloff)
        sound = next(self.iterator)
        sound.set_volume(ratio)
        sound.play()

    @not_executed_when_muted
    def stop(self):
        for sound in self.sounds:
            sound.stop()


class SfxSound():
    def __init__(
            self,
            name,
            filename,
            trigger,
            falloff,
            emitter=None,
            sound=None,
            zone=None):

        self.filename = filename
        self.sound = sound or load_sound(filename)
        self.zone = Rect(*zone) if zone else None
        self.falloff = falloff
        self.emitter = emitter
        self.trigger = trigger

    @not_executed_when_muted
    def play(self):
        position = self.emitter.pixel_center
        ratio = self.zone.falloff_ratio(position, self.falloff)
        self.sound.set_volume(ratio)
        self.sound.play()

    @not_executed_when_muted
    def stop(self):
        self.sound.stop()


class AudioStreamer():
    def __init__(self):
        self.sounds = []
        self.ambiances = []

    @not_executed_when_muted
    def shoot(self, triggers):
        for trigger in triggers:
            for sound in self.sounds:
                if sound.trigger != trigger:
                    continue
                position = sound.emitter.pixel_center
                if sound.zone and sound.zone.contains(position) is False:
                    continue
                sound.play()

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
