
import os
import json
import logging

import corax.context as cctx
from corax.core import RUN_MODES, NODE_TYPES
from corax.crackle.io import load_scripts
from corax.iterators import iter_on_jobs, fade
from corax.gamepad import InputBuffer
from corax.player import load_players
from corax.pygameutils import draw_letterbox, render_background
from corax.scene import build_scene
from corax.seeker import find_start_scrolling_target
from corax.sounds import AudioStreamer


def load_scene_data(data, name):
    """
    This function find the given scene name in the data and build a Scene
    object.
    """
    for scene in data["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(cctx.SCENE_FOLDER, scene["file"])
            with open(file_, "r") as f:
                return json.load(f)
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
        self.players = load_players()
        self.scrolling_target = find_start_scrolling_target(self.players, data)
        self.scripts = load_scripts(self)
        self.script_names_by_zone = {}
        self.current_scripts = []
        self.freeze = 0
        self.set_scene(data["start_scene"])
        self.run_mode = RUN_MODES.NORMAL
        self.script_iterator = None
        self.transition = fade(data["fade_in_duration"], maximum=255, reverse=True)
        self.alpha = 0

    def get_scene(self, scene_name, scene_data):
        return self.loaded_scenes.get(scene_name) or self.loaded_scenes.setdefault(
            scene_name, build_scene(scene_name, scene_data, self))

    def set_scene(self, scene_name):
        # Currently, the engine rebuild each scene from scratch each it is set.
        # This is not a really efficient way but it spares high memory usage.
        # It makes a small freeze between each cut. To avoid that, i should
        # writte a streaming system which pre-load neighbour scenes in a
        # parallel thread and keep in memory as long as the game is suceptible
        # to request it. Let's see if it is possible !
        scene_data = load_scene_data(self.data, scene_name)
        self.scene = self.get_scene(scene_name, scene_data)
        self.scene.scrolling.target = self.scrolling_target
        self.script_names_by_zone = {z: z.script_names for z in self.scene.zones}
        script_names = [n for z in self.scene.zones for n in z.script_names]
        self.current_scripts = []

        for script in self.scripts:
            if script.name in script_names:
                # this rebuilt only the conditions checkers and action runner
                # using the new scene environment. And filter the script which
                # will be evaluated.
                script.build(self)
                self.current_scripts.append(script)

        for player in self.players:
            for slot in self.scene.player_slots:
                if player.name == slot.name:
                    slot.player = player
                    player.coordinate.block_position = slot.block_position
                    player.coordinate.flip = slot.flip
            player.set_no_go_zones([
                z for z in self.scene.zones
                if z.type == NODE_TYPES.NO_GO and
                player.name in z.affect])

        self.audio_streamer.set_scene(scene_data["sounds"], self.scene)

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
        triggerable = self.players + self.scene.animated_sets
        self.audio_streamer.evaluate()
        self.audio_streamer.shoot([t.trigger for t in triggerable])
        self.render(screen)
        self.scene.scrolling.evaluate()

    def evaluate_script_mode(self, joystick):
        try:
            next(self.script_iterator)
        except StopIteration:
            # The script is finished then go back to normal mode.
            if self.run_mode == RUN_MODES.RESTART:
                return
            self.run_mode = RUN_MODES.NORMAL
            self.script_iterator = None
            self.evaluate_normal_mode(joystick)

    def evaluate_normal_mode(self, joystick):
        keystate_changed = self.input_buffer.update(joystick)
        self.parse_and_try_scripts()
        # If script is executed, the run mode is set to SCRIPT.
        if keystate_changed is True and self.run_mode != RUN_MODES.SCRIPT:
            for player in self.players:
                player.input_updated(self.input_buffer)

    def parse_and_try_scripts(self):
        for zone, script_names in self.script_names_by_zone.items():
            if not script_names:
                continue
            for player in self.players:
                conditions = (
                    player.name not in zone.affect or
                    player.pixel_center is None or
                    not zone.contains(pixel_position=player.pixel_center))
                if conditions:
                    continue
                for script_name in script_names:
                    for script in self.current_scripts:
                        if script.name == script_name and script.check():
                            logging.debug(f"SCRIPT: running {script_name}")
                            self.run_script(script)

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
        transition_alpha = 255 - self.alpha
        if transition_alpha:
            render_background(screen, alpha=transition_alpha)