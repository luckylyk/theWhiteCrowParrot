import os
from PySide6 import QtWidgets, QtCore, QtGui


HERE = os.path.dirname(os.path.realpath(__file__))
ICON_FOLDER = os.path.join(HERE, "icons")
icons = {}


def ctrl_pressed():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == (modifiers | QtCore.Qt.ControlModifier)


def shift_pressed():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == (modifiers | QtCore.Qt.ShiftModifier)


def alt_pressed():
    modifiers = QtWidgets.QApplication.keyboardModifiers()
    return modifiers == (modifiers | QtCore.Qt.AltModifier)


def get_icon(filename):
    if icons.get(filename) is None:
        icons[filename] = QtGui.QIcon(os.path.join(ICON_FOLDER, filename))
    return icons[filename]
