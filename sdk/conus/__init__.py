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

app = QtWidgets.QApplication([])

win = MainWindow()

win.show()
app.exec()
