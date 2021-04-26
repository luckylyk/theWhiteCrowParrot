
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)

# initialize project
import corax.context as cctx
GAMEdata_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_data = cctx.initialize(GAMEdata_FOLDER)

for scene in GAME_data["scenes"]:
    if scene["name"] == GAME_data["start_scene"]:
        filename = scene["file"]
scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
with open(scene_filepath, "r") as f:
    scene_data = json.load(f)
for element in scene_data["elements"]:
    if element["type"] != "layer" and not element.get("name"):
            element["name"] = element["file"].split(".")[0]

with open(scene_filepath, "w") as f:
    json.dump(scene_data, f)