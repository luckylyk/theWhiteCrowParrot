import io
import os
import itertools
import numpy as np
from PIL import Image, ImageQt
from PySide6 import QtGui, QtWidgets, QtCore

sheet = f'{os.path.dirname(__file__)}/../whitecrowparrot/animations/whitecrowparrot_banner_body.png'
KEY_COLOR = 0, 255, 0, 255


def spritesheet_to_images(sheetpath, frame_size):
    sheet = QtGui.QImage(sheetpath)
    if not sheet:
        return []
    width, height = frame_size
    row = sheet.height() / height
    col = sheet.width() / width
    index = 0
    for j, i in itertools.product(range(int(row)), range(int(col))):
        x, y = i * width, j * height
        image = sheet.copy(x, y, width, height)
        array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(array)
        buffer.open(QtCore.QIODevice.WriteOnly)
        image.save(buffer, 'png')
        data = bytes(array)
        image = Image.open(io.BytesIO(data)).convert('RGBA')
        data = np.array(image)
        data[(data == KEY_COLOR).all(axis = -1)] = (0, 0, 0, 0)
        image = Image.fromarray(data, mode='RGBA')
        filepath = f'C:/Users/lio/Desktop/zini/exporttest/export.{index}.png'
        image.save(filepath, 'png')
        index += 1


app = QtWidgets.QApplication([])
images = spritesheet_to_images(sheet, [310, 300])
