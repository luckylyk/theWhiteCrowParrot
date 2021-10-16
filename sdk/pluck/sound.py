
from PyQt5 import QtWidgets, QtGui
from corax.core import NODE_TYPES, LOOP_TYPES
from pluck.data import DATA_TEMPLATES
from pluck.parsing import (
    list_all_existing_triggers, list_all_existing_interactors)
from pluck.qtutils import get_icon


SOUND_TYPES = (
    NODE_TYPES.AMBIANCE,
    NODE_TYPES.SFX_COLLECTION,
    NODE_TYPES.SFX,
    NODE_TYPES.MUSIC
)


class FileField(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineedit = QtWidgets.QLineEdit()
        self.browse = QtWidgets.QPushButton(get_icon("folder.png"), "")
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.browse)

    @property
    def value(self):
        return self.lineedit.text()


class FilesField(QtWidgets.QWidget):
    @property
    def value(self):
        return ['']


class ZoneField(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        self.inputs = [QtWidgets.QLineEdit() for _ in range(4)]
        self.layout = QtWidgets.QHBoxLayout(self)

        for input_ in self.inputs:
            input_.setValidator(validator)
            self.layout.addWidget(input_)

    @property
    def value(self):
        return [int(input_.text()) for input_ in self.inputs]

    @value.setter
    def value(self, value):
        assert len(value) == 4 and all(isinstance(n, int) for n in value)
        for i, input_ in enumerate(self.inputs):
            input_.setText(str(value[i]))


class StrField(QtWidgets.QLineEdit):
    @property
    def value(self):
        return self.text()


class TriggerField(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_triggers()))

    @property
    def value(self):
        return self.text()


class IntField(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        self.setValidator(validator)

    @property
    def value(self):
        return int(self.text())


class InteractorField(QtWidgets.QLineEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_interactors()))

    @property
    def value(self):
        return self.text()


class OrderField(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems([LOOP_TYPES.CYCLE, LOOP_TYPES.SHUFFLE])

    @property
    def value(self):
        return self.currentText()


class TypeField(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(SOUND_TYPES)

    @property
    def value(self):
        return self.currentText()


WIDGET_BY_TYPE = {
    "name": StrField,
    "type": TypeField,
    "file": FileField,
    "files": FilesField,
    "channel": IntField,
    "falloff": IntField,
    "order": OrderField,
    "trigger": TriggerField,
    "listener": InteractorField,
    "zone": ZoneField,
    "emitter": InteractorField
}


class CreateSoundDialog(QtWidgets.QDialog):

    def __init__(self, zone=None, parent=None):
        zone = zone or [0, 0, 0, 0]
        super().__init__(parent=parent)
        self.property_widgets = {key: cls() for key, cls in WIDGET_BY_TYPE.items()}
        self.layout = QtWidgets.QFormLayout(self)
        for name, widget in self.property_widgets.items():
            self.layout.addRow(name.capitalize(), widget)

        self.property_widgets["zone"].value = zone
        self.property_widgets["type"].currentTextChanged.connect(self._update_statuses)
        self._update_statuses()

    def _update_statuses(self):
        keys = DATA_TEMPLATES[self.property_widgets["type"].currentText()].keys()
        key = [str(key) for key in keys]
        for key, widget in self.property_widgets.items():
            widget.setVisible(key in keys)

