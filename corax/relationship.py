"""
This module is about how a animation sheet behave automatically.
It's a kind of IA.
"""
import os
import corax.context as cctx
from corax.core import AIM_RELATIONSHIP_TYPES
from corax.hitmap import detect_hitmap_collision
from corax.override import load_json


def load_relationships():
    return [
        load_json(os.path.join(cctx.RELATIONSHIP_FOLDER, filename))
        for filename in os.listdir(cctx.RELATIONSHIP_FOLDER)]


def detect_collision(collisions, subject, target):
    block_position1 = subject.coordinate.block_position
    block_position2 = target.coordinate.block_position
    for collision in collisions:
        hitmap1 = (subject.hitmaps or {}).get(collision["subject_hitmap"], [])
        hitmap2 = (target.hitmaps or {}).get(collision["target_hitmap"], [])
        detection =  detect_hitmap_collision(
            hitmap1, hitmap2, block_position1, block_position2, print_=collision["subject_hitmap"]=="feet")
        if detection:
            return collision["event"]


def build_moves_probabilities(rules, subject, target):
    """
    Look up to the coordinate and animation relationship between the subject
    and the target. This create a dict of moves with a weighting value:
    output:
    {
        "move1": 15,
        "move2": 3,
        "move3": 12,
        "move4": 4
    }
    """
    rules = filter_rules_from_distance(rules, subject, target)
    rules = filter_aim_relationships(rules, subject, target)
    rules = filter_rules_from_animations(rules, subject, target)
    moves = {}
    for rule in rules:
        for move, value in rule['moves'].items():
            moves.setdefault(move, 0)
            moves[move] += value * rule["priority"]
    return moves


def aim_relationships(coordinates1, coordinates2):
    """
    Look up at the position and the flip state of each coordinate and define
    the AIM_RELATIONSHIP_TYPES.
    """
    before = coordinates1.block_position[0] <= coordinates2.block_position[0]
    if coordinates1.flip == coordinates2.flip:
        if before:
            return AIM_RELATIONSHIP_TYPES.TARGET_FROM_BEHIND
        return AIM_RELATIONSHIP_TYPES.SUBJECT_FROM_BEHIND
    if before:
        return AIM_RELATIONSHIP_TYPES.FACING
    return AIM_RELATIONSHIP_TYPES.BACK_TO_BACK


def filter_aim_relationships(rules, subject, target):
    coord1 = subject.coordinate
    coord2 = target.coordinate
    return [
        rule for rule in rules
        if aim_relationships(coord1, coord2) in rule['directions']]


def filter_rules_from_distance(rules, subject, target):
    dist = subject.coordinate.block_center_distance(target.coordinate)
    return [
        rule for rule in rules
        if rule['block_distance_range'] is None or
        (r:=rule['block_distance_range'])[0] <= dist <= r[1]]


def filter_rules_from_animations(rules, subject, target):
    return [
        rule for rule in rules
        if subject.animation.name in rule['subject_animations']
        and target.animation.name in rule['target_animations']]