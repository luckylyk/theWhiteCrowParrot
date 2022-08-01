from lib2to3.pytree import Base
import os
import shutil


PYKRITA_ROOT = os.path.expanduser("~/AppData/Roaming/krita/pykrita")
TO_COPY = f"{os.path.dirname(__file__)}/../extension"

try:
    shutil.rmtree(f'{PYKRITA_ROOT}/kritax')
except BaseException:
    ...
try:
    os.remove(f'{PYKRITA_ROOT}/kritax.desktop')
except BaseException:
    ...

shutil.copytree(f'{TO_COPY}/kritax', f'{PYKRITA_ROOT}/kritax')
shutil.copy(f'{TO_COPY}/kritax.desktop', f'{PYKRITA_ROOT}/kritax.desktop')
