from PyQt5 import QtWidgets


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