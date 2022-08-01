# And add the extension to Krita's list of extensions:
from PyQt5 import QtWidgets
import krita
from .extension import Kritax
from .window import MyDocker

app = krita.Krita.instance()
app.addExtension(Kritax(app))
factory = QtWidgets.DockWidgetFactory(
    "myDocker",
    QtWidgets.DockWidgetFactoryBase.DockRight, MyDocker)
app.addDockWidgetFactory(factory)