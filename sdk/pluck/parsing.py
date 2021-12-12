import os
import json
from pathlib import Path

import corax.context as cctx
from corax.core import NODE_TYPES
import corax.crackle.io

from pluck.data import SOUND_TYPES, ZONE_TYPES


INTERACTOR_TYPES = (
    NODE_TYPES.PLAYER,
    NODE_TYPES.SET_ANIMATED
)


def parse_json_files(directory):
    sheet_files = Path(directory).glob("**/*.json")
    for sheet_file in sheet_files:
        with open(sheet_file, "r") as f:
            yield json.load(f)


def list_all_existing_interactors():
    return sorted(list({
        element.get("name")
        for data in parse_json_files(cctx.SCENE_FOLDER)
        for element in data.get("elements")
        if element.get("type") in INTERACTOR_TYPES and
        element.get("name")}))


def list_all_existing_triggers():
    sheet_triggers = {
        trigger
        for data in parse_json_files(cctx.SHEET_FOLDER)
        for value in data["moves"].values()
        for _, trigger in value.get("triggers") or []}
    scene_triggers = {
        sound["trigger"]
        for data in parse_json_files(cctx.SCENE_FOLDER)
        for sound in data["sounds"]
        if sound.get("trigger")}
    return sorted(list(sheet_triggers | scene_triggers))


def list_all_existing_hitboxes():
    return sorted(list({
        str(value)
        for data in parse_json_files(cctx.SHEET_FOLDER)
        for move in data["moves"].values()
        for value in (move.get("hitboxes") or {}).keys()}))


def list_all_existing_sounds(types=None):
    return sorted([
        sound
        for data in parse_json_files(cctx.SCENE_FOLDER)
        for sound in data["sounds"]
        if sound["type"] in (types or SOUND_TYPES)],
        key=lambda x: x["name"])


def list_all_existing_triggers_sounds():
    triggers_sounds = []
    sfx_sounds = list_all_existing_sounds([NODE_TYPES.SFX])
    for sfx_sound in sfx_sounds:
        trigger = sfx_sound.get("trigger")
        if not trigger:
            continue
        filename = os.path.join(cctx.SOUNDS_FOLDER, sfx_sound["file"])
        triggers_sounds.append((trigger, filename))

    sfx_collections = list_all_existing_sounds([NODE_TYPES.SFX_COLLECTION])
    for sfx_collection in sfx_collections:
        trigger = sfx_collection.get("trigger")
        if not trigger:
            continue
        for file_ in sfx_collection.get("files"):
            filename = os.path.join(cctx.SOUNDS_FOLDER, file_)
            triggers_sounds.append((trigger, filename))

    result = []
    for trigger_sound in triggers_sounds:
        if trigger_sound in result:
            continue
        result.append(trigger_sound)
    return result


def list_all_existing_zones(zone_type=None):
    return sorted([
        zone
        for data in parse_json_files(cctx.SCENE_FOLDER)
        for zone in data["zones"]
        if zone["type"] in (zone_type or ZONE_TYPES)],
        key=lambda x: x["name"])


def list_all_existing_script_names():
    scripts = []
    for filename in os.listdir(cctx.SCRIPT_FOLDER):
        filepath = os.path.join(cctx.SCRIPT_FOLDER, filename)
        namespace = ".".join(filename.split(".")[:-1])
        scripts.extend(corax.crackle.io.parse_crackle_file(filepath, namespace))
    return sorted(list({script.name for script in scripts}))