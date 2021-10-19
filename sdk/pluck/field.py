
from typing import Iterable
from PyQt5 import QtWidgets, QtGui
from pluck.parsing import (
    list_all_existing_triggers, list_all_existing_interactors)
from pluck.qtutils import get_icon


class FileField(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineedit = QtWidgets.QLineEdit()
        self.browse = QtWidgets.QPushButton(get_icon("folder.png"), "")
        self.browse.released.connect(self.import_sound)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.lineedit)
        self.layout.addWidget(self.browse)

    @property
    def value(self):
        return self.lineedit.text()

    @value.setter
    def value(self, value):
        self.lineedit.setText(value)


class FilesField(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.list = QtWidgets.QListWidget()
        mode = QtWidgets.QAbstractItemView.ExtendedSelection
        self.list.setSelectionMode(mode)
        self.browse = QtWidgets.QPushButton(get_icon("folder.png"), "")
        self.browse.released.connect(self.import_sounds)
        self.delete = QtWidgets.QPushButton("X")
        self.delete.released.connect(self.remove_selection)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.setContentsMargins(0, 0, 0, 0)
        self.layout_btn.addStretch(1)
        self.layout_btn.addWidget(self.browse)
        self.layout_btn.addWidget(self.delete)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.list)
        self.layout.addLayout(self.layout_btn)

    @property
    def value(self):
        return [self.list.item(i).text() for i in range(self.list.count())]

    @value.setter
    def value(self, value):
        self.list.clear()
        self.list.addItems(value)

    def remove_selection(self):
        items = self.list.selectedItems()
        if not items:
            return
        for item in items:
            self.list.takeItem(self.list.row(item))


class ZoneField(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        self.inputs = [QtWidgets.QLineEdit() for _ in range(4)]
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        for input_ in self.inputs:
            input_.setValidator(validator)
            self.layout.addWidget(input_)

    @property
    def value(self):
        return [int(input_.text() or 0) for input_ in self.inputs]

    @value.setter
    def value(self, value):
        assert len(value) == 4 and all(isinstance(n, int) for n in value)
        for i, input_ in enumerate(self.inputs):
            input_.setText(str(value[i]))


class StrField(QtWidgets.QLineEdit):
    @property
    def value(self):
        value = self.text()
        if "," not in value:
            return value
        return [v.strip(" ") for v in value.split(",")]

    @value.setter
    def value(self, value):
        if isinstance(value, (list, tuple)):
            value = ", ".join(value)
        self.setText(value)



class TriggerField(StrField):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_triggers()))


class IntField(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        self.setValidator(validator)

    @property
    def value(self):
        return int(self.text() or 0)

    @value.setter
    def value(self, value):
        self.setText(str(value))


class InteractorField(StrField):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_interactors()))


class ComboField(QtWidgets.QComboBox):
    ITEMS = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(self.ITEMS)

    @property
    def value(self):
        return self.currentText()

    @value.setter
    def value(self, value):
        self.setCurrentText(value)


class OptionField(QtWidgets.QWidget):
    def __init__(self, name, cls, parent=None):
        super().__init__()
        self.name = QtWidgets.QLabel(name)
        self.widget = cls()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.widget)

    @property
    def value(self):
        return self.widget.value

    @value.setter
    def value(self, value):
        self.widget.value = value

    def set_label_width(self, width):
        self.name.setFixedWidth(width)