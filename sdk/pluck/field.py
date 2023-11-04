
import os
from functools import partial
from PySide6 import QtWidgets, QtGui, QtCore
import corax.context as cctx

from corax.core import LOOP_TYPES
from pluck.data import ZONE_TYPES, plain_text_to_data, data_to_plain_text
from pluck.dialog import ColorDialog
from pluck.highlighter import CoraxHighlighter, RULES
from pluck.parsing import (
    list_all_existing_triggers, list_all_existing_interactors,
    list_all_existing_event_names, list_all_existing_script_names)
from pluck.qtutils import get_icon
from pluck.sanity import is_valid_animation_path


DEFAULT_RESOLUTIONS = ["800, 600", "1024, 1080", "640, 480", "1920, 1080"]


class FieldPanel(QtWidgets.QWidget):
    edited = QtCore.Signal()
    fieldEdited = QtCore.Signal(str)

    def __init__(self, fields, parent=None):
        super().__init__(parent=parent)
        self._fields = {name: widget() for name, widget in fields.items()}

        self.form = QtWidgets.QFormLayout()
        self.form.setSpacing(0)

        for name, widget in self._fields.items():
            widget.edited.connect(self.edited.emit)
            widget.edited.connect(partial(self.fieldEdited.emit, name))
            name = f'{name.capitalize().replace("_", " ")}: '
            self.form.addRow(name, widget)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.form)
        self.layout.addStretch(1)

    @property
    def fields(self):
        return self._fields

    @property
    def values(self):
        return {k: w.value for k, w in self._fields.items()}

    @values.setter
    def values(self, values):
        self.blockSignals(True)
        for k, v in values.items():
            if not self._fields.get(k):
                continue
            self._fields[k].value = v
        self.blockSignals(False)


class OptionField(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, name, cls, parent=None):
        super().__init__(parent=parent)
        self.name = QtWidgets.QLabel(name)
        self.widget = cls()
        self.widget.edited.connect(self.edited.emit)
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


class ComboField(QtWidgets.QComboBox):
    edited = QtCore.Signal()
    ITEMS = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentTextChanged.connect(self._changed_emit)
        self.addItems(self.ITEMS)

    def _changed_emit(self, *_):
        self.edited.emit()

    @property
    def value(self):
        return self.currentText()

    @value.setter
    def value(self, value):
        self.setCurrentText(value)


class ExistingStringsField(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, strings, parent=None):
        super().__init__(parent)
        mode = QtWidgets.QAbstractItemView.ExtendedSelection
        self.list1 = QtWidgets.QListWidget()
        self.list1.setSelectionMode(mode)
        self.list2 = QtWidgets.QListWidget()
        self.list2.setSelectionMode(mode)
        self.list2.addItems(strings)

        self.add = QtWidgets.QPushButton("Add")
        self.add.released.connect(self.call_add)
        self.remove = QtWidgets.QPushButton("Remove")
        self.remove.released.connect(self.call_remove)

        self.list_layout = QtWidgets.QHBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addWidget(self.list1)
        self.list_layout.addWidget(self.list2)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addWidget(self.add)
        self.button_layout.addWidget(self.remove)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.list_layout)
        self.layout.addLayout(self.button_layout)

    def call_add(self):
        items = self.list2.selectedItems()
        if not items:
            return
        self.list1.addItems([i.text() for i in items])
        self.edited.emit()

    def call_remove(self):
        items = self.list1.selectedItems()
        if not items:
            return
        for item in items:
            self.list1.takeItem(self.list1.row(item))
        self.edited.emit()

    @property
    def value(self):
        return [self.list1.item(i).text() for i in range(self.list1.count())]

    @value.setter
    def value(self, value):
        self.list1.clear()
        self.list1.addItems(value)


class ScriptsField(ExistingStringsField):

    def __init__(self):
        super().__init__(list_all_existing_script_names())


class EventsField(ExistingStringsField):

    def __init__(self):
        super().__init__(list_all_existing_event_names())


class TypeField(ComboField):
    ITEMS = ZONE_TYPES


class FileField(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineedit = QtWidgets.QLineEdit()
        self.browse = QtWidgets.QPushButton(get_icon("folder.png"), "")
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
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list = QtWidgets.QListWidget()
        mode = QtWidgets.QAbstractItemView.ExtendedSelection
        self.list.setSelectionMode(mode)
        self.browse = QtWidgets.QPushButton(get_icon("folder.png"), "")
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
        self.edited.emit()


def ensure_linux_path(path):
    return path.replace("\\", "/")


def strip_sound_root(path):
    root = os.path.normpath(cctx.SOUNDS_FOLDER)
    path = os.path.normpath(path)
    return ensure_linux_path(path[len(root):].strip("\\/"))


class SoundFileField(FileField):

    def import_sound(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open sound", cctx.SOUNDS_FOLDER, "Sounds (*.wav *.ogg )")[0]
        if not path:
            return
        if os.path.normpath(cctx.SOUNDS_FOLDER) not in os.path.normpath(path):
            return
        self.lineedit.setText(strip_sound_root(path))


class SoundFilesField(FilesField):
    def import_sounds(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Open sound", cctx.SOUNDS_FOLDER, "Sounds (*.wav *.ogg )")[0]
        if not paths:
            return
        for path in paths:
            if os.path.normpath(cctx.SOUNDS_FOLDER) not in os.path.normpath(path):
                continue
            self.list.addItem(strip_sound_root(path))


class ZoneField(QtWidgets.QWidget):
    edited = QtCore.Signal()

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
            input_.returnPressed.connect(self.edited.emit)

    @property
    def value(self):
        return [int(input_.text() or 0) for input_ in self.inputs]

    @value.setter
    def value(self, value):
        assert len(value) == 4 and all(isinstance(n, int) for n in value), str(value)
        for i, input_ in enumerate(self.inputs):
            input_.setText(str(value[i]))


class StrField(QtWidgets.QLineEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.returnPressed.connect(self.edited.emit)

    @property
    def value(self):
        return self.text().strip(" ") or None

    @value.setter
    def value(self, value):
        self.setText(value)


class StrArrayField(QtWidgets.QLineEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.returnPressed.connect(self.edited.emit)

    @property
    def value(self):
        return [v.strip(" ") for v in self.text().split(",")] or None

    @value.setter
    def value(self, value):
        if not value:
            self.setText("")
            return
        self.setText(", ".join(value))


class TriggerField(StrField):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_triggers()))


class IntField(QtWidgets.QLineEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.returnPressed.connect(self.edited.emit)
        validator = QtGui.QIntValidator()
        self.setValidator(validator)

    @property
    def value(self):
        return int(self.text() or 0)

    @value.setter
    def value(self, value):
        self.setText(str(value))


class FloatField(QtWidgets.QLineEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.returnPressed.connect(self.edited.emit)
        validator = QtGui.QDoubleValidator()
        self.setValidator(validator)

    @property
    def value(self):
        return float(self.text().replace(',', '.') or 0.0)

    @value.setter
    def value(self, value):
        self.setText(str(value))


class InteractorField(StrField):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCompleter(QtWidgets.QCompleter(list_all_existing_interactors()))


class InteractorsField(InteractorField):

    @property
    def value(self):
        return [super().value]


class ColorField(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rgb = [0, 0, 0]
        self.labels = [QtWidgets.QLabel() for _ in range(3)]
        self.button = QtWidgets.QPushButton()
        self.button.setFixedHeight(15)
        self.button.released.connect(self._set_color)
        self.layout = QtWidgets.QHBoxLayout(self)
        for label in self.labels:
            self.layout.addWidget(label)
        self.layout.addWidget(self.button)

    def _set_color(self):
        dialog = ColorDialog(self.rgb)
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return
        self.rgb = dialog.rgb
        self.value = dialog.rgb
        self.edited.emit()

    @property
    def value(self):
        return self.rgb

    @value.setter
    def value(self, value):
        self.rgb = value
        r, g, b = value
        for label, c, v in zip(self.labels, "rgb", (r, g, b)):
            label.setText(f"{c}:{v}")
        self.button.setStyleSheet(f'background-color: #{r:02x}{g:02x}{b:02x}')


class IntVectorComboField(ComboField):
    ITEMS = DEFAULT_RESOLUTIONS

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setEditable(True)

    @property
    def value(self):
        return [int(n) for n in self.currentText().split(",")]

    @value.setter
    def value(self, value):
        self.setCurrentText(",".join(str(v).strip(" ") for v in value))


class IntArrayField(QtWidgets.QLineEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.returnPressed.connect(self._text_changed)

    def _text_changed(self):
        if self.is_valid():
            self.edited.emit()

    def is_valid(self):
        try:
            [int(n) for n in self.text().split(",")]
            return True
        except:
            pass
        return False

    @property
    def value(self):
        if self.is_valid():
            return [int(n) for n in self.text().split(",")]
        return 0, 0

    @value.setter
    def value(self, value):
        self.setText(", ".join(str(v).strip(" ") for v in value))


class OrderField(ComboField):
    ITEMS = LOOP_TYPES.CYCLE, LOOP_TYPES.SHUFFLE



class IntVectorField(IntArrayField):
    edited = QtCore.Signal()

    def is_valid(self):
        try:
            if len([int(n) for n in self.text().split(",")]) == 2:
                return True
        except:
            pass
        return False


class LayersField(QtWidgets.QWidget):
    edited = QtCore.Signal()
    stateChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = QtWidgets.QTableView()
        self.layers.horizontalHeader().show()
        mode = QtWidgets.QHeaderView.ResizeToContents
        self.layers.horizontalHeader().setSectionResizeMode(mode)
        self.layers.horizontalHeader().setStretchLastSection(True)
        self.layers.setShowGrid(False)
        self.layers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.layers.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.layers.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.layers.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.layers.setAlternatingRowColors(True)
        self.layers.verticalHeader().hide()
        mode = QtWidgets.QHeaderView.ResizeToContents
        self.layers.verticalHeader().setSectionResizeMode(mode)
        self.model = LayerFieldTableModel()
        self.model.dataChanged.connect(self.edited.emit)
        self.model.stateChanged.connect(self.stateChanged.emit)
        self.layers.setModel(self.model)

        self.add = QtWidgets.QPushButton("Add")
        self.add.released.connect(self.add_item)
        self.remove = QtWidgets.QPushButton("Remove")
        self.remove.released.connect(self.remove_selection)
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.add)
        self.btn_layout.addWidget(self.remove)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.layers)
        self.layout.addLayout(self.btn_layout)

    def remove_selection(self):
        index_list = []
        for model_index in self.layers.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)

        for index in index_list:
            self.model.remove_row(index.row())
        self.edited.emit()

    def add_item(self):
        self.model.add_row("item", "*.png")
        self.edited.emit()

    @property
    def value(self):
        return {v[0]: v[1] for v in self.model.values}

    @value.setter
    def value(self, value):
        self.model.clear()
        for name, path in value.items():
            self.model.add_row(name, path)

    @property
    def filenames(self):
        return [
            v[1] for i, v in enumerate(self.model.values)
            if self.model.states[i]]


class LayerFieldTableModel(QtCore.QAbstractTableModel):
    dataChanged = QtCore.Signal()
    stateChanged = QtCore.Signal()
    HEADERS = "Name", "File"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._data = []
        self._states = []

    @property
    def values(self):
        return self._data

    @property
    def states(self):
        return self._states

    @property
    def names(self):
        return [d[0] for d in self._data]

    def rowCount(self, _=None):
        return len(self._data)

    def columnCount(self, _):
        return 2

    def get_unique_name(self, basename):
        names = self.names
        name = basename
        i = 0
        while name in names:
            name = f'{basename}_{i:02d}'
            i += 1
        return name

    def add_row(self, name="", path=""):
        self.layoutAboutToBeChanged.emit()
        name = self.get_unique_name(name)
        self._data.append([name, path])
        self._states.append(True)
        self.layoutChanged.emit()

    def clear(self):
        self.layoutAboutToBeChanged.emit()
        self._data = []
        self._states = []
        self.layoutChanged.emit()

    def remove_row(self, i):
        self.layoutAboutToBeChanged.emit()
        del self._data[i]
        del self._states[i]
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.HEADERS[section]

    def flags(self, index):
        flags = QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if index.column() == 0:
            flags |= QtCore.Qt.ItemIsUserCheckable
        return flags

    def setData(self, index, value, role):
        if role == QtCore.Qt.CheckStateRole:
            if sum(self._states) <= 1 and value == QtCore.Qt.Unchecked:
                return False
            self._states[index.row()] = value == QtCore.Qt.Checked
            self.stateChanged.emit()
            return True
        if value == self.data(index, QtCore.Qt.DisplayRole):
            return False
        if index.column() == 0:
            value = self.get_unique_name(value)
        self._data[index.row()][index.column()] = value
        self.dataChanged.emit()
        return True

    def data(self, index, role):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        if role == QtCore.Qt.CheckStateRole and col == 0:
            return QtCore.Qt.Checked if self._states[row] else QtCore.Qt.Unchecked
        elif role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            return self._data[row][col]
        elif role == QtCore.Qt.BackgroundRole:
            if not is_valid_animation_path(self._data[row][1]):
                return QtGui.QColor('red')


class BoolField(ComboField):
    ITEMS = ["true", "false"]

    @property
    def value(self):
        return self.currentIndex() == 0

    @value.setter
    def value(self, value):
        return self.setCurrentIndex(int(not bool(value)))


class DictField(QtWidgets.QPlainTextEdit):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        doc = self.document()
        self.highlighter = CoraxHighlighter(RULES["json"], document=doc)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.textChanged.connect(self._update)
        self.setFixedHeight(45)

    def _update(self):
        try:
            text = "{" + self.toPlainText() + "}"
            plain_text_to_data(text)
            self.edited.emit()
        except:
            pass

    @property
    def value(self):
        try:
            text = "{" + self.toPlainText().replace("\n", ",").strip(",") + "}"
            result =  plain_text_to_data(text)
            return result
        except:
            return {}

    @value.setter
    def value(self, value):
        text = "\n".join([f.strip(", ") for f in data_to_plain_text(value).strip("{}").split("\n") if f])
        self.setPlainText(text)