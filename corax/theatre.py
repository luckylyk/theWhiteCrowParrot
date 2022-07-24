
import itertools
import os
import logging

import corax.context as cctx
from corax.core import CHARACTER_TYPES, RUN_MODES, NODE_TYPES
from corax.character import load_characters
from corax.crackle.io import load_crackle_objects
from corax.hitmap import hitmap_collide_zone
from corax.iterators import iter_on_jobs, fade, choose
from corax.gamepad import InputBuffer
from corax.override import load_json
from corax.pygameutils import draw_letterbox, render_background
from corax.relationship import (
    build_moves_probabilities, load_relationships, detect_collision)
from corax.scene import build_scene
from corax.seeker import find_relationship, find_start_scrolling_targets, find
from corax.sounds import AudioStreamer


def load_scene_data(data, name):
    """
    This function find the given scene name in the data and build a Scene
    object.
    """
    for scene in data["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(cctx.SCENE_FOLDER, scene["file"])
            return load_json(file_)
    raise ValueError(f'Scene "{name}" not found in the game data')


class Theatre:
    """
    This is the main game class controller. It manage the run mode: normal,
    pause or script. It manage the scene transitions, the script
    execution and the global variable (not implemented yet).
    Simplyfied map off the Corax engine workflow.

            ----------------------> Theatre <-----------------
           /               ---->---/   |                       \
          /               /            v                        \
         /      InputBuffer            |                         \
        /         |       ________ RUN_MODES                      \
       /          |      /      ____/  |                           \
      /          /      v      /       v                           |
     /          /    NORMAL   |      SCRIPT                        |
    |          /       | \    ^                                    |
  Player--<---         ^  v   |                                    |
    | |                |   \   \                                   |
    | |              Scene  \   \                                  |
    | |               /|\    CrackleScript -----<---\              |
    | |              / | \____________________       \             |
    | |         ____/  \                      \       \            |
    | |        |        \---- scene_2          |       \           |
    | |     scene_1           ^  ^           scene_3    |          |
    | |                   ___/   |                      |          |
    | ^                  /      Zone                    |          |
    | \               Layers        \                   |          |
    |  \             /  |   \        \                  |    AudioStreamer
    |   \           /   |  Particles  |                 |          |
    |    \---PlayerSlot |             |                 |          |
    |                   v             |                 |        Ambiance
    |           SetAnimatedElement    |                 |  Sfx, SfxCollection
    |            SetStaticElement     /\               /
    |                                /  \_____________/
     \                              /
      \-->--AnimationController--<-/
                   |       \
                   v        \
              Spritesheet    ^
                    \        |
                     v       |
                    Animations
    """
    def __init__(self, data):
        self.data = data
        self.globals = data["globals"]
        self.scene = None

        self.loaded_scenes = {}
        self.input_buffer = InputBuffer()
        self.audio_streamer = AudioStreamer()

        chars = load_characters()
        self.characters = chars
        self.players = [c for c in chars if c.type == CHARACTER_TYPES.PLAYER]
        self.npcs = [c for c in chars if c.type == CHARACTER_TYPES.NPC]
        self.relationships = load_relationships()

        self.scrolling_targets = find_start_scrolling_targets(chars, data)
        self.scripts, events = load_crackle_objects()
        self.events = {e.name: e for e in events}
        self.current_scripts = []
        self.freeze = 0
        self.set_scene(data["start_scene"])
        self.run_mode = RUN_MODES.NORMAL
        self.script_iterator = None
        self.event_iterators = {}
        self.checkpoint_requested = False
        duration = data["fade_in_duration"]
        trans = fade(duration, maximum=255, reverse=True) if duration else None
        self.transition = trans
        self.alpha = 0 if self.transition else 255

    @property
    def evaluables(self):
        return self.characters + self.npcs + self.scene.animated_sets

    def get_scene(self, scene_name, scene_data):
        return (
            self.loaded_scenes.get(scene_name) or
            self.loaded_scenes.setdefault(
                scene_name, build_scene(scene_name, scene_data)))

    def set_scene(self, scene_name):
        # Currently, the engine rebuild each scene from scratch each it is set.
        # This is not a really efficient way but it spares high memory usage.
        # It makes a small freeze between each cut. To avoid that, i should
        # writte a streaming system which pre-load neighbour scenes in a
        # parallel thread and keep in memory as long as the game is suceptible
        # to request it. Let's see if it is possible !
        scene_data = load_scene_data(self.data, scene_name)
        self.scene = self.get_scene(scene_name, scene_data)
        self.scene.scrolling.targets = self.scrolling_targets
        self.init_scene_scripts()
        self.init_scene_characters()
        self.audio_streamer.set_scene(scene_data["sounds"], self.scene)

    def init_scene_scripts(self):
        script_names = [n for z in self.scene.zones for n in z.script_names]
        self.current_scripts = []
        for script in self.scripts:
            if script.name in script_names:
                # this rebuilt only the conditions checkers and action runner
                # using the new scene environment. And filter the script which
                # will be evaluated.
                script.build(self)
                self.current_scripts.append(script)

    def init_scene_characters(self):
        for character in self.characters:
            for slot in self.scene.player_slots + self.scene.npc_slots:
                if character.name == slot.name:
                    slot.character = character
                    character.coordinate.block_position = slot.block_position
                    character.coordinate.flip = slot.flip

            if character.type == NODE_TYPES.PLAYER:
                character.set_no_go_zones([
                    z for z in self.scene.zones
                    if z.type == NODE_TYPES.NO_GO and
                    character.name in z.affect])

    def evaluate(self, joystick, screen):
        if not self.scene:
            raise ValueError("No scene set")
        if self.freeze > 0:
            self.freeze -= 1
        elif self.run_mode == RUN_MODES.NORMAL:
            self.evaluate_normal_mode(joystick)
        elif self.run_mode == RUN_MODES.SCRIPT:
            self.evaluate_script_mode(joystick)
        if self.freeze:
            return

        self.scene.evaluate()
        triggerable = self.scene.animated_sets + self.characters
        self.audio_streamer.evaluate()
        self.audio_streamer.shoot([t.trigger for t in triggerable])
        self.render(screen)
        self.scene.scrolling.evaluate()

    def evaluate_script_mode(self, joystick):
        try:
            next(self.script_iterator)
        except StopIteration:
            # The script is finished then go back to normal mode.
            if self.run_mode in (RUN_MODES.RESTART, RUN_MODES.RESTORE):
                return
            self.run_mode = RUN_MODES.NORMAL
            self.script_iterator = None
            self.evaluate_normal_mode(joystick)

    def evaluate_normal_mode(self, joystick):
        keystate_changed = self.input_buffer.update(joystick)
        # If script is executed, the run mode is set to SCRIPT.
        if not self.scene:
            return

        for zone in self.scene.zones:
            match zone.type:
                case NODE_TYPES.NO_GO:
                    continue
                case NODE_TYPES.INTERACTION:
                    self.evaluate_interactions(zone)
                case NODE_TYPES.RELATIONSHIP:
                    if not zone.enable:
                        continue
                    self.evaluate_relationship(zone)
                case NODE_TYPES.COLLIDER:
                    self.evaluate_collision(zone)
                case NODE_TYPES.EVENT_ZONE:
                    self.evaluate_trigger(zone)
        self.evaluate_events()

        if keystate_changed is True and self.run_mode != RUN_MODES.SCRIPT:
            for player in self.players:
                player.input_updated(self.input_buffer)

    def evaluate_relationship(self, zone):
        # Detect assosiated relationship
        subject = find(self.evaluables, zone.subject)
        target = find(self.evaluables, zone.target)
        if None in (subject, target):
            return

        relationship = find_relationship(self.relationships, zone.relationship)
        if not relationship:
            return
        # Check collision event.
        event = detect_collision(relationship["collisions"], subject, target)
        if event and (event not in self.event_iterators):
            self.queue_event(event)

        rules = relationship["rules"]
        probabilities = build_moves_probabilities(rules, subject, target)
        if not probabilities:
            return
        move = choose(probabilities)
        subject.animation_controller.propose_moves([move])

    def evaluate_events(self):
        if not self.event_iterators:
            return
        for name, iterator in tuple(self.event_iterators.items()):
            try:
                next(iterator)
            except StopIteration:
                del self.event_iterators[name]

    def evaluate_collision(self, zone):
        for evaluable in self.evaluables:
            conditions = (
                evaluable.name in zone.affect and
                evaluable.hitmaps and
                list(hitmaps:=set(list(evaluable.hitmaps)) & set(zone.hitmaps)))

            if not conditions:
                continue

            for hitmap in hitmaps:
                block_position = evaluable.coordinate.block_position
                hitmap = evaluable.hitmaps[hitmap]
                if hitmap_collide_zone(hitmap, zone, block_position):
                    event = zone.event
                    self.queue_event(event)
                    return

    def evaluate_trigger(self, zone):
        if not (event_names := zone.event_names):
            return

        target = find(self.evaluables, zone.target) if zone.target else None
        for evaluable in self.evaluables:
            conditions = (
                evaluable.name not in zone.affect or
                evaluable.trigger is None or
                evaluable.trigger != zone.trigger or
                evaluable.pixel_center is None or
                not zone.contains(pixel_position=evaluable.pixel_center))
            if target and target.pixel_center:
                zonale = zone.contains(pixel_position=target.pixel_center)
                conditions = conditions or not zonale

            if conditions:
                continue

            for event in event_names:
                logging.debug(
                    f"Event: {event}: trigger={evaluable.trigger}"
                    f"->character:{evaluable.name}")
                self.queue_event(event)

    def evaluate_interactions(self, zone):
        if not (script_names := zone.script_names):
            return

        for evaluable in self.evaluables:
            conditions = (
                evaluable.name not in zone.affect or
                evaluable.pixel_center is None or
                not zone.contains(pixel_position=evaluable.pixel_center))

            if conditions:
                continue

            iterator = itertools.product(script_names, self.current_scripts)
            for script_name, script in iterator:
                if script.name == script_name and script.check():
                    logging.debug(f"SCRIPT: running {script_name}")
                    self.run_script(script)

    def queue_event(self, event):
        crackle_event = self.events[event]
        jobs = crackle_event.jobs(self)
        actions = crackle_event.actions
        self.event_iterators[event] = iter_on_jobs(jobs, actions=actions)

    def run_script(self, script):
        jobs = script.jobs(self)
        self.script_iterator = iter_on_jobs(jobs, script.actions)
        self.run_mode = RUN_MODES.SCRIPT

    def pause(self):
        self.audio_streamer.pause()

    def resume(self):
        self.audio_streamer.resume()

    def render(self, screen):
        if not self.scene:
            raise RuntimeError("Can't render a theatre with no scene runnging")

        self.scene.render(screen)
        draw_letterbox(screen)

        if self.transition:
            try:
                self.alpha = next(self.transition)
            except StopIteration:
                self.transition = None

        if transition_alpha := 255 - self.alpha:
            render_background(screen, alpha=transition_alpha)
