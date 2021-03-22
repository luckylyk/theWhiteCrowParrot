from distutils.core import setup
import py2exe

setup(
    name="Corax Engine",
    author="Lionel Brouyère",
    author_email="lionel.brouyere@gmail.com",
    console=['corax/__main__.py'])

import os
import shutil

command = '"corax/corax.exe" data --fullscreen'
current = os.path.dirname(__file__)
desktop = os.path.expanduser("~/Desktop")
src = os.path.join(current, "dist")
gameroot = os.path.join(desktop, "whitecrowparrot")
dst = os.path.join(gameroot, "corax")

os.makedirs(gameroot)
shutil.move(src, dst)
os.rename(os.path.join(dst, "__main__.exe"), os.path.join(dst, "corax.exe"))

shutil.copytree(
    src=os.path.join(current, "whitecrowparrot"),
    dst=os.path.join(gameroot, "data"))

with open(os.path.join(gameroot, "whitecrowparrot.bat"), "w") as f:
    f.write(command)