from PyQt5 import QtWidgets


class GameKicker(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Launch the game")
        self.debug_mode = QtWidgets.QCheckBox("Debug render mode")
        self.mute = QtWidgets.QCheckBox("Muted")
        self.mute.setChecked(True)
        self.fullscreen = QtWidgets.QCheckBox("Fullscreen")
        self.scaled = QtWidgets.QCheckBox("Scaled render")
        self.scaled.setChecked(True)
        self.skip_splash = QtWidgets.QCheckBox("Skip splash screen")

        self.kick = QtWidgets.QPushButton("Kick")
        self.kick.released.connect(self.accept)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.debug_mode)
        self.layout.addWidget(self.mute)
        self.layout.addWidget(self.fullscreen)
        self.layout.addWidget(self.scaled)
        self.layout.addWidget(self.skip_splash)
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
        return arguments