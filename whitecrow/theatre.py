
import os
import json

from whitecrow.scene import build_scene
from whitecrow.gamepad import InputBuffer
from whitecrow.constants import SCENE_FOLDER


def find_scene(datas, name, input_buffer):
    for scene in datas["scenes"]:
        if scene["name"] == name:
            file_ = os.path.join(SCENE_FOLDER, scene["file"])
            with open(file_, "r") as f:
                d = json.load(f)
            return build_scene(d, input_buffer)


class Theatre:
    def __init__(self, datas):
        self.input_buffer = InputBuffer()
        self.datas = datas
        self.caption = datas["caption"]
        self.scene = find_scene(datas, datas["start_scene"], self.input_buffer)

