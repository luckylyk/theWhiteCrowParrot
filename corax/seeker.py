
def find_player(theatre, name):
    for player in theatre.players:
        if player.name == name:
            return player


def find_start_scrolling_target(players, data):
    for player in players:
        if player.name == data["start_scrolling_target"]:
            return player.coordinate


def find_element(scene, name):
    for element in scene.elements:
        if element.name == name:
            return element


def find_animated_set(scene, name):
    for element in scene.animated_sets:
        if element.name == name:
            return element


def find_zone(scene, name):
    for zone in scene.zones:
        if zone.name == name:
            return zone