# Command to build: python setup.py build

import sys
from cx_Freeze import setup, Executable


build_exe_options = {
    "excludes": [
        "tkinter", "numpy", "scipy", "unittest", "urllib", "http", "html",
        "unicodedata", "email", "pkg_resources", "xml", "pydoc_data",
        "pyexpat", "ctypes"]}

setup(
    name="Corax Engine",
    author="Lionel Brouyère",
    author_email="lionel.brouyere@gmail.com",
    options = {"build_exe": build_exe_options},
    executables=[Executable('corax/__main__.py')])


import os
import shutil

command = '"corax/corax.exe" data -o "overrides\\fight.ovr"'
current = os.path.dirname(__file__)
desktop = os.path.expanduser("~/Desktop")
gameroot = os.path.join(desktop, "whitecrowparrot")
src = os.path.join(current, "build/exe.win-amd64-3.10")
dst = os.path.join(gameroot, "corax")

os.makedirs(gameroot)
shutil.move(src, dst)
os.rename(os.path.join(dst, "__main__.exe"), os.path.join(dst, "corax.exe"))

shutil.copytree(
    src=os.path.join(current, "whitecrowparrot"),
    dst=os.path.join(gameroot, "data"))

with open(os.path.join(gameroot, "whitecrowparrot.bat"), "w") as f:
    f.write(command)
