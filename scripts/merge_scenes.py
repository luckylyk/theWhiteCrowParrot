import os
import json

root = f'{os.path.dirname(os.path.dirname(__file__))}/whitecrowparrot'
scenes = ['scenes/hives.json', 'scenes/forest_01.json']
output = 'scenes/merge.json'

block_size = 10


scenes_data = []
for scene in scenes:
    with open(f'{root}/{scene}', 'r') as f:
        scenes_data.append(json.load(f))


def merge_boundaries(scenes_data):
    left = min(scene['boundary'][0] for scene in scenes_data)
    top = min(scene['boundary'][1] for scene in scenes_data)
    right = sum(scene['boundary'][2] for scene in scenes_data)
    bottom = max(scene['boundary'][3] for scene in scenes_data)
    return [left, top, right, bottom]


def merge_soft_boundaries(scenes_data):
    offset = 0
    boundaries = []
    for scene_data in scenes_data:
        for boundary in scene_data['soft_boundaries']:
            boundaries.append([
                boundary[0] + offset, boundary[1],
                boundary[2] + offset, boundary[3]])
        offset = scene_data['boundary'][2]
    return boundaries


def merge_zones(scenes_data):
    offset = 0
    results = []
    for scene_data in scenes_data:
        for zone in scene_data['zones']:
            zone = zone.copy()
            zone['zone'][0] += (offset // block_size)
            zone['zone'][2] += (offset // block_size)
            results.append(zone)
        offset = scene_data['boundary'][2]
    return results


def merge_sounds(scenes_data):
    offset = 0
    results = []
    for scene_data in scenes_data:
        for sound in scene_data['sounds']:
            sound = sound.copy()
            if not sound['zone']:
                results.append(sound)
                continue
            sound['zone'][0] += offset
            sound['zone'][2] += offset
            results.append(sound)
        offset = scene_data['boundary'][2]
    return results


def merge_elements(scenes_data):
    offset = 0
    results = []
    for scene_data in scenes_data:
        for element in scene_data['elements']:
            match element['type']:
                case 'layer':
                    results.append(element.copy())
                case 'set_static':
                    bg = element.copy()
                    bg['position'][0] += offset
                    results.append(bg)
                case 'particles_system':
                    pc = element.copy()
                    pc['zone'][0] += offset
                    pc['zone'][2] += offset
                    results.append(pc)
                case 'set_animated':
                    ani = element.copy()
                    ani['position'][0] += offset
                    results.append(ani)
                case 'player':
                    ply = element.copy()
                    ply['block_position'][0] += (offset // block_size)
                    results.append(ply)
                case 'npc':
                    npc = element.copy()
                    npc['block_position'][0] += (offset // block_size)
                    results.append(npc)
        offset = scene_data['boundary'][2]
    return results


merged_scene = {
    'name': 'forest',
    'type': 'scene',
    'background_color': scenes_data[0]['background_color'],
    'boundary': merge_boundaries(scenes_data),
    'target_offset': scenes_data[0]['target_offset'],
    'soft_boundaries': merge_soft_boundaries(scenes_data),
    'sounds': merge_sounds(scenes_data),
    'zones': merge_zones(scenes_data),
    'elements': merge_elements(scenes_data)
}


with open(f'{root}/{output}', 'w') as f:
    json.dump(merged_scene, f, indent=2)
