
import json
from pathlib import Path

import corax.context as cctx
from corax.core import NODE_TYPES

from pluck.data import SOUND_TYPES


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
    return sorted(list({
        trigger
        for data in parse_json_files(cctx.SHEET_FOLDER)
        for value in data["moves"].values()
        for _, trigger in value.get("triggers") or []}))


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