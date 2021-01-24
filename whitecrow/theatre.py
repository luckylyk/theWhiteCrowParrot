
import os
import json

import whitecrow.context as wctx
from whitecrow.scene import build_scene
from whitecrow.gamepad import InputBuffer


def find_scene(datas, name, input_buffer):
    for scene in datas["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(wctx.SCENE_FOLDER, scene["file"])
            with open(file_, "r") as f:
                d = json.load(f)
            return build_scene(name, d, input_buffer)


class Theatre:
    def __init__(self, datas):
        self.input_buffer = InputBuffer()
        self.datas = datas
        self.caption = datas["caption"]
        self.scene = find_scene(datas, datas["start_scene"], self.input_buffer)

    def next(self):
        next_true = False
        for scene in self.datas["scenes"]:
            if next_true:
                self.scene = find_scene(
                    self.datas,
                    scene["name"],
                    self.input_buffer)
                return
            if scene["name"] == self.scene.name:
                next_true = True
        self.scene = find_scene(
            self.datas,
            self.datas["scenes"][0]["name"],
            self.input_buffer)

