
def find_player(theatre, name):
    for player in theatre.players:
        if player.name == name:
            return player
    raise ValueError(f"Player '{name}' not found")


def find_start_scrolling_target(players, data):
    name = data["start_scrolling_target"]
    for player in players:
        if player.name == name:
            return player.coordinate
    raise ValueError(f"Target '{name}' not found")


def find_element(scene, name):
    for element in scene.elements:
        if element.name == name:
            return element
    raise ValueError(f"Element '{name}' not found in {scene.name}\n{[e.name for e in scene.elements]}")


def find_animated_set(scene, name):
    for element in scene.animated_sets:
        if element.name == name:
            return element
    raise ValueError(f"Animated set '{name}' not found in {scene.name}")


def find_zone(scene, name):
    for zone in scene.zones:
        if zone.name == name:
            return zone