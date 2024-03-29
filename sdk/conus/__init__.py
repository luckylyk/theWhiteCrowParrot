# generate environment
import os
import sys


HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{HERE}/../../..')
sys.path.append(f'{HERE}/../..')
sys.path.append(f'{HERE}/..')


from conus.coraxutils import init_corax

init_corax(sys.argv[1])

from conus.main import MainWindow
from PySide6 import QtWidgets


with open(f'{HERE}/flatdark.css', 'r') as f:
    style = f.read()
app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(style)
win = MainWindow()
win.show()
sys.exit(app.exec())
