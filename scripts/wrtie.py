a = """lg_fg_grass 1604 237
lg_fg_tree_01 1439 0
lg_fg_tree_02 1737 0
fg_sl_grass_01 0 156
fg_sl_grass_02 0 188
fg_grass_02 769 154
fg_hanging_01 2020 0
fg_hanging_02 2017 0
fg_grass_03 1700 239
fg_small_tree 1063 196
fg_small_grass 974 236
"""

for line in a.split("\n"):
    if not line:
        continue
    name = line.split(" ")[0]
    x = int(line.split(" ")[1])
    y = int(line.split(" ")[2])
    print (f"""
{{
    "file": "/level_01/{name}.png",
    "position": [{x}, {y}],
    "elevation": 0
}},""")