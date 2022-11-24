import os
import glob
import json

folder = f'{os.path.dirname(__file__)}/../whitecrowparrot/sheets'

jsons = glob.glob(f'{folder}/*.json')
jsons.extend(glob.glob(f'{folder}/*/*.json'))

for filename in jsons:
    with open(filename, 'r') as f:
        data = json.load(f)
    for move in data['moves'].values():
        if move['loop_on'] is None:
            move['loop_on'] = [[]]
    with open(filename, 'w') as f:
        json.dump(data, f)