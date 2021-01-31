
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)

# initialize project
import corax.context as cctx
GAMEDATAS_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_DATAS = cctx.initialize(GAMEDATAS_FOLDER)

for scene in GAME_DATAS["scenes"]:
    if scene["name"] == GAME_DATAS["start_scene"]:
        filename = scene["file"]
scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
with open(scene_filepath, "r") as f:
    scene_datas = json.load(f)
for element in scene_datas["elements"]:
    if element["type"] != "layer" and not element.get("name"):
            element["name"] = element["file"].split(".")[0]

with open(scene_filepath, "w") as f:
    json.dump(scene_datas, f)