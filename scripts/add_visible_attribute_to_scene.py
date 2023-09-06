
import os
import json
root = r'D:\Works\code\GitHub\theWhiteCrowParrot\whitecrowparrot\scenes'
filenames = os.listdir(root)
for filename in filenames:
    if os.path.splitext(filename)[-1] != '.json':
        continue
    jsonfile = f'{root}/{filename}'
    with open(jsonfile, 'r') as f:
        scene = json.load(f)
    for element in scene['elements']:
        if element.get('type') == 'set_animated':
            element['visible'] = element.get('visible', True)
    with open(jsonfile, 'w') as f:
        json.dump(scene, f, indent=2)