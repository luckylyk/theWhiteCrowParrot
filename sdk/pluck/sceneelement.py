from PySide6 import QtWidgets
from pluck.field import (
    IntField, StrField, FloatField, FileField, BoolField, IntVectorField,
    FieldPanel)


KEY_FIELDS = {
    "name": StrField,
    "deph": FloatField,
    "file": FileField,
    "block_position": IntVectorField,
    "position": IntVectorField,
    "flip": BoolField,
    "alpha": IntField,
}


class SceneElementFields(FieldPanel):
    def __init__(self, data, parent=None):
        self.data = data
        fields = {k: v for k, v in KEY_FIELDS.items() if k in data}
        super().__init__(fields, parent)
        self.values = data

    @property
    def values(self):
        self.data.update({k: w.value for k, w in self._fields.items()})
        return self.data

    @values.setter
    def values(self, values):
        for k, v in values.items():
            if not self._fields.get(k):
                continue
            self._fields[k].value = v


class SceneElementDialog(QtWidgets.QDialog):
    def __init__(self, data):
        super().__init__()
        self.fields = SceneElementFields(data)
        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.released.connect(self.reject)
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.ok)
        self.button_layout.addWidget(self.cancel)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.fields)
        self.layout.addLayout(self.button_layout)

    @property
    def values(self):
        return self.fields.values
