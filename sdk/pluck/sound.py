
from PySide6 import QtWidgets

import corax.context as cctx

from pluck.data import DATA_TEMPLATES, SOUND_TYPES
from pluck.field import (
    OptionField, ZoneField, StrField, TriggerField,
    IntField, InteractorField, ComboField, SoundFileField, SoundFilesField,
    OrderField)
from pluck.parsing import list_all_existing_sounds


WINDOW_TITLE = "Create sound for scene"


class TypeField(ComboField):
    ITEMS = SOUND_TYPES


WIDGET_BY_TYPE = {
    "type": TypeField,
    "name": StrField,
    "file": SoundFileField,
    "files": SoundFilesField,
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
        super().__init__(parent=parent)
        self.setWindowTitle(WINDOW_TITLE)
        zone = zone or [0, 0, 0, 0]
        self.property_widgets = {
            key: OptionField(key.capitalize() + ": ", cls)
            for key, cls in WIDGET_BY_TYPE.items()}
        self.sound_type = self.property_widgets["type"].widget

        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.released.connect(self.reject)

        self.existing_sounds = QtWidgets.QListWidget()
        self.existing_sounds.itemSelectionChanged.connect(self.sound_selected)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.addWidget(self.ok)
        self.layout_btn.addWidget(self.cancel)

        self.prop_layout = QtWidgets.QVBoxLayout()
        for widget in self.property_widgets.values():
            self.prop_layout.addWidget(widget)
            widget.set_label_width(75)
        self.prop_layout.addStretch(1)

        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.addLayout(self.prop_layout)
        self.top_layout.addWidget(self.existing_sounds)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.layout_btn)

        self.property_widgets["zone"].value = [int(n * cctx.BLOCK_SIZE) for n in zone]
        self.sound_type.currentTextChanged.connect(self._update_statuses)
        self._update_statuses()

    def _update_statuses(self):
        sound_type = self.sound_type.currentText()
        keys = DATA_TEMPLATES[sound_type].keys()
        key = [str(key) for key in keys]
        for key, widget in self.property_widgets.items():
            widget.setVisible(key in keys)

        sounds = list_all_existing_sounds([sound_type])
        self.existing_sounds.clear()
        for sound in sounds:
            item = QtWidgets.QListWidgetItem(sound["name"])
            item.sound = sound
            self.existing_sounds.addItem(item)

    def sound_selected(self):
        items = self.existing_sounds.selectedItems()
        if not items:
            return
        for k, v in items[0].sound.items():
            if k == "zone":
                continue
            self.property_widgets[k].value = v

    @property
    def result(self):
        keys = DATA_TEMPLATES[self.sound_type.currentText()].keys()
        return {key: self.property_widgets[key].value for key in keys}
