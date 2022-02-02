
from PySide6 import QtWidgets, QtCore
from pluck.field import (
    FieldPanel, StrField, IntField, ColorField, IntVectorComboField,
    StrArrayField)


GAME_SETTINGS_FIELDS = {
    "title": StrField,
    "start_scene": StrField,
    "start_scrolling_targets": StrArrayField,
    "fade_in_duration": IntField
}


PEFERENCES_FIELDS = {
    "resolution": IntVectorComboField,
    "fps": IntField,
    "block_size": IntField,
    "key_color": ColorField,
    "camera_speed": IntField
}


class ProjectManager(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = FieldPanel(GAME_SETTINGS_FIELDS)
        self._settings.edited.connect(self.edited.emit)
        self._preferences = FieldPanel(PEFERENCES_FIELDS)
        self._preferences.edited.connect(self.edited.emit)
        self.tab = QtWidgets.QTabWidget()
        self.tab.addTab(self._settings, "Project Settings")
        self.tab.addTab(self._preferences, "Preferences")
        self.data_traceback = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.tab)
        self.layout.addWidget(self.data_traceback)

    @property
    def settings(self):
        return self._settings.values

    @settings.setter
    def settings(self, values):
        self._settings.values = values

    @property
    def preferences(self):
        return self._preferences.values

    @preferences.setter
    def preferences(self, values):
        self._preferences.values = values

    def set_error(self, text):
        self.data_traceback.setText(text)
        self.data_traceback.setStyleSheet("background-color:red")

    def clean_error(self):
        self.data_traceback.setText("")
        self.data_traceback.setStyleSheet("")