
import os
import shutil


SOURCES_PATH = os.path.join(os.path.dirname(__file__), '../sdk/krita/extensions')
DEPLOY_PATH = 'C:/Program Files/Krita (x64)/share/krita/pykrita'


for file_ in os.listdir(SOURCES_PATH):
    src = os.path.join(SOURCES_PATH, file_)
    dst = os.path.join(DEPLOY_PATH, file_)
    if not os.path.isdir(src):
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(src, dst)
        continue

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
