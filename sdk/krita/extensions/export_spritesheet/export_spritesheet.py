
from krita import Extension, Krita
from PyQt5 import QtWidgets, QtCore

_exporter = None
def show():
    global _exporter
    if not _exporter:
        _exporter = QtWidgets.QWidget()
        _exporter.setWindowFlags(QtCore.Qt.Tool)
    _exporter.show()


class MyExtension(Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("corax_exporter", "Prout", "tools/scripts")
        action.triggered.connect(show)


# And add the extension to Krita's list of extensions:
print("fuckyou")
Krita.instance().addExtension(MyExtension(Krita.instance()))