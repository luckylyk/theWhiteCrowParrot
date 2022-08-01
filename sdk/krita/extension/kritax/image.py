from PyQt5 import QtGui


def remove_key_color(image, key_color):
    for i in range(image.width()):
        for j in range(image.height()):
            color = image.pixelColor(i, j)
            if color == key_color:
                image.setPixelColor(i, j, QtGui.QColor(0, 0, 0, 0))