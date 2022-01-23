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


def find_start_scrolling_target(players, data):
    target = find(players, name:=data["start_scrolling_target"])
    if not target:
        raise ValueError(f"Target '{name}' not found")
    return target


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