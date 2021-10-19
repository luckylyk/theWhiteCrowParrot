from PyQt5 import QtWidgets, QtCore
from pluck.parsing import list_all_existing_triggers
from pluck.qtutils import get_icon


class GameKicker(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Launch the game")
        self.debug_mode = QtWidgets.QCheckBox("Debug render mode")
        self.mute = QtWidgets.QCheckBox("Muted")
        self.fullscreen = QtWidgets.QCheckBox("Fullscreen")
        self.fullscreen.setChecked(True)
        self.scaled = QtWidgets.QCheckBox("Scaled render")
        self.skip_splash = QtWidgets.QCheckBox("Skip splash screen")
        self.skip_splash.setChecked(True)
        self.fast_fps = QtWidgets.QCheckBox("Double Speed")

        self.kick = QtWidgets.QPushButton("Kick")
        self.kick.released.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.debug_mode)
        self.layout.addWidget(self.mute)
        self.layout.addWidget(self.fullscreen)
        self.layout.addWidget(self.scaled)
        self.layout.addWidget(self.skip_splash)
        self.layout.addWidget(self.fast_fps)
        self.layout.addWidget(self.kick)

    def arguments(self):
        arguments = []
        if self.debug_mode.isChecked():
            arguments.append("--debug")
        if self.mute.isChecked():
            arguments.append("--mute")
        if self.fullscreen.isChecked():
            arguments.append("--fullscreen")
        if self.scaled.isChecked():
            arguments.append("--scaled")
        if self.skip_splash.isChecked():
            arguments.append("--skip_splash")
        if self.fast_fps.isChecked():
            arguments.append("--speedup")
        return arguments


class TriggerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)
        self.triggers = QtWidgets.QComboBox()
        self.triggers.addItems(list_all_existing_triggers())
        self.triggers.setEditable(True)
        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.released.connect(self.reject)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.addWidget(self.ok)
        self.layout_btn.addWidget(self.cancel)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.triggers)
        self.layout.addLayout(self.layout_btn)

    @property
    def trigger(self):
        return self.triggers.currentText()


class CreateOnSceneDialog(QtWidgets.QDialog):

    def __init__(self, zone=None, parent=None):
        super().__init__(parent=parent)
        zone = zone or []
        self.zone = zone
        self.result = None
        text = "zone selected: {}".format(", ".join(str(z) for z in zone))
        self.label = QtWidgets.QLabel(text)
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.create_sound = QtWidgets.QPushButton("Create Sound")
        self.create_sound.released.connect(self._call_create_sound)
        self.create_zone = QtWidgets.QPushButton("Create Zone")
        self.create_zone.released.connect(self._call_create_zone)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.addWidget(self.create_sound)
        self.layout_btn.addWidget(self.create_zone)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.layout_btn)

    def _call_create_sound(self):
        self.result = "sounds"
        self.accept()

    def _call_create_zone(self):
        self.result = "zones"
        self.accept()

