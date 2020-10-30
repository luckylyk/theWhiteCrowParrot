import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA_FOLDER = os.path.join(ROOT, "data")
ANIMATION_FOLDER = os.path.join(DATA_FOLDER, "animations")
MOVE_FOLDER = os.path.join(DATA_FOLDER, "moves")

OPTIONS = {
    "resolution": (640, 268),
    "fps": 30,
    "grid_size": 10
}