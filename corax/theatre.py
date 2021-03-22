
import os
import json
import logging

import corax.context as cctx
from corax.core import RUN_MODE
from corax.scene import build_scene
from corax.gamepad import InputBuffer
from corax.crackle.io import load_scripts
from corax.iterators import iter_on_jobs


def find_scene(data, name, input_buffer):
    """
    This function find the given scene name in the data and build a Scene
    object.
    """
    for scene in data["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(cctx.SCENE_FOLDER, scene["file"])
            with open(file_, "r") as f:
                d = json.load(f)
            return build_scene(name, d, input_buffer)


class Theatre:
    """
    This is the main game class controller. It manage the run mode: normal,
    pause or script. It manage the scene transitions, the script
    execution and the global variable (not implemented yet).
    Simplyfied map off the Corax engine workflow.

                       ------------> Theatre
                     /                 |
                    |                  v
                InputBuffer            |
                 /        ________ RUN_MODES______
                /        /      ____/  |          \
               /        v      /       v           \
              /      NORMAL   |   RUN_MODE.SCRIPT   |
             /         ^ \    ^                     v
            /          |  v   |                 RUN_MODE.MENU
           /           |   \   \
          /          Scene  \   \
         /            /|\    CrackleScript -----<--------\
        |            / | \____________________            \
        |       ____/  \                      \            \
        |      |        \---- scene_2---       |            \
        |   scene_1           ^  ^       \   scene_3         \
        |                ____/   |        \                   \
        |               /       Zone       v                   \
        |             Layers        \       \                   \
        |            /  |   \        \        SoundShooter       \
        \          /    |  Particles  |           |               |
         \---> Player   |             |           v               |
               /        v             |        Ambiance           |
              | SetAnimatedElement    |     Sfx, SfxCollection    |
              ^  SetStaticElement     /\                          /
              |                      /  \________________________/
               \                    /
            MovementManager ---<---/
                   |       \
                   v        \
              Spritesheet    ^
                    \        |
                     v       |
                    Animations
    """
    def __init__(self, data):
        self.input_buffer = InputBuffer()
        self.data = data
        self.caption = data["caption"]
        self.globals = data["globals"]
        self.scene = None
        self.scripts = load_scripts()
        self.script_names_by_zone = {}
        self.current_scripts = []
        self.freeze = 0
        for script in self.scripts:
            script.theatre = self
        self.set_scene(data["start_scene"])
        self.run_mode = RUN_MODE.NORMAL
        self.script_iterator = None

    def set_scene(self, scene_name):
        # Currently, the engine rebuild each scene from scratch each it is set.
        # This is not a really efficient way but it spare high memory usage.
        # It makes a small freeze between every cut. To avoid that, i should
        # writte a streaming system which pre-load neightgour scene in a
        # parrallel thread and keep it memory as long as the game is suceptible
        # to request it. Let's see if it is possible !
        self.scene = find_scene(self.data, scene_name, self.input_buffer)
        if self.scene is None:
            raise KeyError(f"{scene_name} scene does'nt exists in the game")
        self.current_scripts = []
        zones = self.scene.zones
        self.script_names_by_zone = {z: z.script_names for z in zones}
        script_names = [n for z in zones for n in z.script_names]
        for script in self.scripts:
            if script.name in script_names:
                # this rebuilt only the conditions checkers and action runner
                # using the new scene environment. And filter the script which
                # will be evaluated.
                script.build()
                self.current_scripts.append(script)

    def evaluate(self, joystick, screen):
        if self.freeze > 0:
            self.freeze -= 1
            return
        if self.run_mode == RUN_MODE.NORMAL:
            self.evaluate_normal_mode(joystick, screen)
        elif self.run_mode == RUN_MODE.SCRIPT:
            self.evaluate_script_mode(joystick, screen)

    def evaluate_script_mode(self, joystick, screen):
        try:
            next(self.script_iterator)
        except StopIteration:
            # the script is finished then go back to normal
            self.run_mode = RUN_MODE.NORMAL
            self.script_iterator = None
            self.evaluate_normal_mode(joystick, screen)
            return
        for element in self.scene.evaluables:
            element.evaluate()
        self.scene.render(screen)
        self.scene.scrolling.evaluate()

    def evaluate_normal_mode(self, joystick, screen):
        for player in self.scene.players:
            player.update_inputs(joystick)
        for element in self.scene.evaluables:
            element.evaluate()
        self.scene.render(screen)
        self.scene.scrolling.evaluate()

        for zone, script_names in self.script_names_by_zone.items():
            if not script_names:
                continue
            for player in self.scene.players:
                conditions = (
                    zone not in player.zones or
                    not zone.contains(pixel_position=player.pixel_center))
                if conditions:
                    continue
                for script_name in script_names:
                    for script in self.current_scripts:
                        if script.name == script_name and script.check():
                            logging.debug(f"SCRIPT: running {script_name}")
                            self.run_script(script)
                            break

    def run_script(self, script):
        self.script_iterator = iter_on_jobs(script.jobs())
        self.run_mode = RUN_MODE.SCRIPT

