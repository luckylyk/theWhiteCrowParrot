# generate environment
import os
import sys
import json

HERE = os.path.dirname(os.path.realpath(__file__))
MAIN_FOLDER = os.path.join(HERE, "..", "..")
SDK_FOLDER = os.path.join(HERE, "..")
sys.path.append(MAIN_FOLDER)
sys.path.append(SDK_FOLDER)

# initialize project
import corax.context as cctx
GAMEDATA_FOLDER = os.path.join(MAIN_FOLDER, "whitecrowparrot")
GAME_data = cctx.initialize(["", GAMEDATA_FOLDER])


def load_spritesheet(filename):
    path = os.path.join(cctx.SHEET_FOLDER, filename)
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    from PyQt5 import QtWidgets, QtCore, QtGui
    from pluck.scene import SceneEditor
    from pluck.highlighter import get_plaint_text_editor
    from pluck.css import get_css
    from pluck.sprite import AnimationDataEditor
    from pluck.main import PluckMainWindow

    for scene in GAME_data["scenes"]:
        if scene["name"] == 'tente':
            filename = scene["file"]
    scene_filepath = os.path.join(cctx.SCENE_FOLDER, filename)
    with open(scene_filepath, "r") as f:
        scene_data = json.load(f)

    app = QtWidgets.QApplication([])

    scene = SceneEditor(scene_data, cctx)

    codesample = os.path.join(cctx.SCRIPT_FOLDER, "forest.ckl")
    with open(codesample, "r") as f:
        text = f.read()

    script, h = get_plaint_text_editor("crackle")
    script.setPlainText(text)

    window = PluckMainWindow()
    window.set_workspace(os.path.realpath(GAMEDATA_FOLDER))
    window.add_scene("tente", scene)
    window.add_script("forest.ckl", script)
    window.add_spritesheet("rabbit", AnimationDataEditor(load_spritesheet("whitecrowparrot_death.json")))
    window.add_spritesheet("tente door", AnimationDataEditor(load_spritesheet("arbaletist.json")))
    window.add_spritesheet("chest_props", AnimationDataEditor(load_spritesheet("whitecrowparrot_collects_sword.json")))
    window.add_spritesheet("chest_props", AnimationDataEditor(load_spritesheet("sword_holder.json")))
    window.add_spritesheet("wcp exploration", AnimationDataEditor(load_spritesheet("whitecrowparrot_exploration.json")))
    window.add_spritesheet("wcp sword", AnimationDataEditor(load_spritesheet("whitecrowparrot_sword.json")))
    window.add_spritesheet("wcp appearing", AnimationDataEditor(load_spritesheet("whitecrowparrot_appearing.json")))
    window.add_spritesheet("chest", AnimationDataEditor(load_spritesheet("chest.json")))
    window.add_spritesheet("chest_armor", AnimationDataEditor(load_spritesheet("chest_armor.json")))
    window.add_spritesheet("chest_flail", AnimationDataEditor(load_spritesheet("chest_flail.json")))
    window.add_spritesheet("chest_bag", AnimationDataEditor(load_spritesheet("chest_bag.json")))
    window.add_spritesheet("chest_locker", AnimationDataEditor(load_spritesheet("chest_locker.json")))
    window.add_spritesheet("chest_props", AnimationDataEditor(load_spritesheet("chest_props.json")))
    window.show()

    stylesheet = get_css("flatdark.css")
    app.setStyleSheet(stylesheet)
    app.exec_()