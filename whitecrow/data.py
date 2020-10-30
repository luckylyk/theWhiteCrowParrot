
import json
import os
from whitecrow.options import ANIMATION_FOLDER


def get_animation_data(filename):
    with open(os.path.join(ANIMATION_FOLDER, filename)) as f:
        return json.load(f)


def list_animation_data_available():
    return [f for f in os.listdir(ANIMATION_FOLDER) if f.endswith(".json")]