
import os
import json
import logging

import corax.context as cctx
from corax.core import RUN_MODE, NODE_TYPES
from corax.crackle.io import load_scripts
from corax.iterators import iter_on_jobs
from corax.gamepad import InputBuffer
from corax.player import load_players
from corax.scene import build_scene
from corax.seeker import find_player, find_start_scrolling_target
from corax.sounds import AudioStreamer


def load_scene_data(data, name, theatre):
    """
    This function find the given scene name in the data and build a Scene
    object.
    """
    for scene in data["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(cctx.SCENE_FOLDER, scene["file"])
            with open(file_, "r") as f:
                return json.load(f)


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
        /         |       ________ RUN_MODES______                \
       /          |      /      ____/  |          \                \
      /          /      v      /       v           \               |
     /          /    NORMAL   |   RUN_MODE.SCRIPT   |              |
    |          /       | \    ^                     v              |
  Player--<---         ^  v   |                 RUN_MODE.MENU      |
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
        self.caption = data["caption"]
        self.globals = data["globals"]
        self.scene = None
        self.input_buffer = InputBuffer()
        self.audio_streamer = AudioStreamer()
        self.players = load_players()
        self.scrolling_target = find_start_scrolling_target(self.players, data)
        self.scripts = load_scripts(self)
        self.script_names_by_zone = {}
        self.current_scripts = []
        self.freeze = 0
        self.set_scene(data["start_scene"])
        self.run_mode = RUN_MODE.NORMAL
        self.script_iterator = None

    def set_scene(self, scene_name):
        # Currently, the engine rebuild each scene from scratch each it is set.
        # This is not a really efficient way but it spares high memory usage.
        # It makes a small freeze between each cut. To avoid that, i should
        # writte a streaming system which pre-load neighbour scenes in a
        # parallel thread and keep in memory as long as the game is suceptible
        # to request it. Let's see if it is possible !
        scene_data = load_scene_data(self.data, scene_name, self)
        self.scene = build_scene(scene_name, scene_data, self)
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
        if self.freeze > 0:
            self.freeze -= 1
        elif self.run_mode == RUN_MODE.NORMAL:
            self.evaluate_normal_mode(joystick, screen)
        elif self.run_mode == RUN_MODE.SCRIPT:
            self.evaluate_script_mode(joystick, screen)

        if self.freeze:
            return
        self.scene.evaluate()
        self.audio_streamer.evaluate()
        self.audio_streamer.shoot([p.trigger for p in self.players])
        self.scene.render(screen)
        self.scene.scrolling.evaluate()

    def evaluate_script_mode(self, joystick, screen):
        try:
            next(self.script_iterator)
        except StopIteration:
            # The script is finished then go back to normal mode.
            self.run_mode = RUN_MODE.NORMAL
            self.script_iterator = None
            self.evaluate_normal_mode(joystick, screen)

    def evaluate_normal_mode(self, joystick, screen):
        keystate_changed = self.input_buffer.update(joystick)
        self.parse_and_try_scripts()
        # If script is executed, the run mode is set to SCRIPT.
        if keystate_changed is True and self.run_mode != RUN_MODE.SCRIPT:
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
        self.script_iterator = iter_on_jobs(jobs)
        self.run_mode = RUN_MODE.SCRIPT
