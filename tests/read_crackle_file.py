import sys
import os

HERE = os.path.dirname(__file__)

sys.path.append(os.path.realpath(os.path.join(HERE, "..")))

import corax.context as wctx
wctx.initialize(os.path.realpath(os.path.join(HERE, "..", "data")))

from corax.crackle import read_crackle_file

scripts = read_crackle_file("forest.ckl")
for script in scripts:
    print (script)
