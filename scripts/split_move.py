import copy
import json
import os
import shutil


sheet = r""
move = "attack2"
new_move = "attack3"
split_frame = 6

shutil.copy(sheet, f'{os.path.splitext(sheet)[0]} - copy.json')


with open(sheet, "r") as f:
    data = json.load(f)

index = data["evaluation_order"].index(move)
data["evaluation_order"].insert(index + 1, new_move)

move2 = copy.deepcopy(data["moves"][move])
data["moves"][move]["next_move"] = new_move
move2["start_at_image"] = data["moves"][move]["start_at_image"] + split_frame

if data["moves"][move]["frames_centers"]:
    data["moves"][move]["frames_centers"] = move2["frames_centers"][:split_frame]
    move2["frames_centers"] = move2["frames_centers"][split_frame:]

data["moves"][move]["frames_per_image"] = move2["frames_per_image"][:split_frame]
move2["frames_per_image"] = move2["frames_per_image"][split_frame:]

for name, frames in move2["hitmaps"].items():
    data["moves"][move]["hitmaps"][name] = frames[:split_frame]
    move2["hitmaps"][name] = frames[split_frame:]

data["moves"][move]["post_events"] = {}
move2["pre_events"] = {}
data["moves"][new_move] = move2


with open(sheet, "w") as f:
    json.dump(data, f, indent=2)


print("done")