"""
This module contains helpers to filter and find element inside the game
data structure.
"""


def find(array, name):
    for item in array:
        if item.name == name:
            return item


def find_player(theatre, name):
    player = find(theatre.players, name)
    if not player:
        raise ValueError(f"Player '{name}' not found")
    return player


def find_emitter(theatre, name):
    emitter = find(theatre.scene.special_effects, name)
    if not emitter:
        raise ValueError(f"Special effects emitter '{name}' not found")
    return emitter


def find_character(theatre, name):
    character = find(theatre.characters, name)
    if not character:
        raise ValueError(f"Character '{name}' not found")
    return character


def find_start_scrolling_targets(animables, data):
    names = data["start_scrolling_targets"]
    targets = [find(animables, name) for name in names]
    if not targets:
        raise ValueError(f"No targets found '{names}' not found")
    return targets


def find_element(scene, name):
    element = find(scene.elements, name)
    if not element:
        elts = [e.name for e in scene.elements]
        raise ValueError(f"Element '{name}' not found in {scene.name}\n{elts}")
    return element


def find_animated_set(scene, name):
    element = find(scene.elements, name)
    if not element:
        raise ValueError(f"Animated set '{name}' not found in {scene.name}")
    return element


def find_zone(scene, name):
    return find(scene.zones, name)


def find_relationship(relationships, name):
    for relationship in relationships:
        if relationship["name"] == name:
            return relationship
