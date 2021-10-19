from PyQt5 import QtWidgets, QtGui
from pluck.data import DATA_TEMPLATES, ZONE_TYPES
from pluck.field import ZoneField, StrField, InteractorField, ComboField, OptionField
from pluck.parsing import list_all_existing_script_names, list_all_existing_zones


WINDOW_TITLE = "Create Zone"


class ScriptsField(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        mode = QtWidgets.QAbstractItemView.ExtendedSelection
        self.list1 = QtWidgets.QListWidget()
        self.list1.setSelectionMode(mode)
        self.list2 = QtWidgets.QListWidget()
        self.list2.setSelectionMode(mode)
        self.list2.addItems(list_all_existing_script_names())

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

    def call_remove(self):
        items = self.list1.selectedItems()
        if not items:
            return
        for item in items:
            self.list1.takeItem(self.list1.row(item))

    @property
    def value(self):
        return [self.list1.item(i).text() for i in range(self.list1.count())]

    @value.setter
    def value(self, value):
        self.list1.clear()
        self.list1.addItems(value)

class TypeField(ComboField):
    ITEMS = ZONE_TYPES


WIDGET_BY_TYPE = {
    "type": TypeField,
    "name": StrField,
    "affect": InteractorField,
    "scripts": ScriptsField,
    "zone": ZoneField
}


class CreateZoneDialog(QtWidgets.QDialog):

    def __init__(self, zone=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(WINDOW_TITLE)
        zone = zone or [0, 0, 0, 0]
        self.property_widgets = {
            key: OptionField(key.capitalize() + ": ", cls)
            for key, cls in WIDGET_BY_TYPE.items()}
        self.zone_type = self.property_widgets["type"].widget

        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.released.connect(self.reject)

        self.existing_zones = QtWidgets.QListWidget()
        self.existing_zones.itemSelectionChanged.connect(self.zone_selected)

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
        self.top_layout.addWidget(self.existing_zones)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.layout_btn)

        self.property_widgets["zone"].value = zone
        self.zone_type.currentTextChanged.connect(self._update_statuses)
        self._update_statuses()

    def _update_statuses(self):
        zone_type = self.zone_type.currentText()
        keys = DATA_TEMPLATES[zone_type].keys()
        key = [str(key) for key in keys]
        for key, widget in self.property_widgets.items():
            widget.setVisible(key in keys)

        zones = list_all_existing_zones([zone_type])
        self.existing_zones.clear()
        for zone in zones:
            item = QtWidgets.QListWidgetItem(zone["name"])
            item.zone = zone
            self.existing_zones.addItem(item)

    def zone_selected(self):
        items = self.existing_zones.selectedItems()
        if not items:
            return
        for k, v in items[0].zone.items():
            if k == "zone":
                continue
            self.property_widgets[k].value = v

    @property
    def result(self):
        keys = DATA_TEMPLATES[self.zone_type.currentText()].keys()
        return {key: self.property_widgets[key].value for key in keys}

