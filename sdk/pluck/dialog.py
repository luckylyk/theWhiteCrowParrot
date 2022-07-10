from itertools import cycle
from functools import partial
import os
from PySide6 import QtWidgets, QtCore
import pygame
import corax.context as cctx
from corax.animation import animation_index_to_data_index
from pluck.parsing import (
    list_all_existing_triggers, list_all_existing_triggers_sounds,
    list_all_project_files)
from pluck.preference import save_preference, get_preference
from pluck.color import ColorWheel


class GameKicker(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Launch the game")
        self.debug_mode = QtWidgets.QCheckBox("Debug render mode")
        self.debug_mode.setChecked(get_preference("debug_mode", False))
        self.mute = QtWidgets.QCheckBox("Muted")
        self.mute.setChecked(get_preference("muted", False))
        self.fullscreen = QtWidgets.QCheckBox("Fullscreen")
        self.fullscreen.setChecked(get_preference("fullscreen", True))
        self.scaled = QtWidgets.QCheckBox("Scaled render")
        self.scaled.setChecked(get_preference("scaled", False))
        self.skip_splash = QtWidgets.QCheckBox("Skip splash screen")
        self.skip_splash.setChecked(get_preference("skip_splash", True))
        self.fast_fps = QtWidgets.QCheckBox("Double Speed")
        self.fast_fps.setChecked(get_preference("fast_fps", False))
        self.overrides = QtWidgets.QLineEdit()
        self.overrides.setText(get_preference("overrides", ""))

        self.kick = QtWidgets.QPushButton("Kick")
        self.kick.released.connect(self.accept)
        self.kick.released.connect(self.save_preferences)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.debug_mode)
        self.layout.addWidget(self.mute)
        self.layout.addWidget(self.fullscreen)
        self.layout.addWidget(self.scaled)
        self.layout.addWidget(self.skip_splash)
        self.layout.addWidget(self.fast_fps)
        self.layout.addWidget(self.overrides)
        self.layout.addWidget(self.kick)

    def save_preferences(self):
        save_preference("debug_mode", self.debug_mode.isChecked())
        save_preference("muted", self.mute.isChecked())
        save_preference("fullscreen", self.fullscreen.isChecked())
        save_preference("scaled", self.scaled.isChecked())
        save_preference("skip_splash", self.skip_splash.isChecked())
        save_preference("fast_fps", self.fast_fps.isChecked())
        save_preference("overrides", self.overrides.text())

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
        if self.overrides.text():
            path = os.path.join(cctx.ROOT, self.overrides.text())
            arguments.append("--overrides")
            arguments.append(path)
        return arguments


class TriggerDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select trigger")
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
        self.create_sound.released.connect(partial(self._call_create, "sounds"))
        self.create_zone = QtWidgets.QPushButton("Create Zone")
        self.create_zone.released.connect(partial(self._call_create, "zones"))
        self.create_soft_boundary = QtWidgets.QPushButton("Add soft boundary")
        method = partial(self._call_create, "soft_boundaries")
        self.create_soft_boundary.released.connect(method)

        self.layout_btn = QtWidgets.QGridLayout()
        self.layout_btn.addWidget(self.create_sound, 0, 0)
        self.layout_btn.addWidget(self.create_zone, 0, 1)
        self.layout_btn.addWidget(self.create_soft_boundary, 1, 0, 1, 2)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addLayout(self.layout_btn)

    def _call_create(self, type_):
        self.result = type_
        self.accept()


class CreateRessourceFileDialog(QtWidgets.QDialog):
    def __init__(self, filename, name=None, parent=None):
        super().__init__(parent)
        self.has_name = bool(name)
        if name:
            self._name = QtWidgets.QLineEdit(name)
        self._filename = QtWidgets.QLineEdit(filename)

        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.cancel = QtWidgets.QPushButton("Cancel")
        self.cancel.released.connect(self.reject)

        self.form = QtWidgets.QFormLayout()
        if self.has_name:
            self.form.addRow("Name", self._name)
        self.form.addRow("Filename", self._filename)

        self.layout_btn = QtWidgets.QHBoxLayout()
        self.layout_btn.addWidget(self.ok)
        self.layout_btn.addWidget(self.cancel)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.form)
        self.layout.addLayout(self.layout_btn)

    @property
    def name(self):
        if not self.has_name:
            return ""
        return self._name.text()

    @property
    def filename(self):
        return self._filename.text()


class LineTestDialog(QtWidgets.QDialog):

    def __init__(self, data, images, animation_viewer, parent=None):
        super().__init__(parent)
        pygame.mixer.init()
        self.setWindowTitle("Linetest")

        self.data = data
        self.animation_viewer = animation_viewer
        self.list = QtWidgets.QListWidget()
        self.images = images
        self.items = []
        self.index = cycle(range(sum(data['frames_per_image'])))
        self.prev_index = None

        triggers = [t[1] for t in data['triggers'] or []]
        for trigger, filename in list_all_existing_triggers_sounds():
            if trigger not in triggers:
                continue
            sound = pygame.mixer.Sound(filename)
            filename = os.path.basename(filename)
            item = QtWidgets.QListWidgetItem(f'{trigger} - {filename}')
            item.trigger = trigger
            item.sound = sound
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.list.addItem(item)
            self.items.append(item)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.animation_viewer)
        self.layout.addWidget(self.list)

        self.timer = QtCore.QBasicTimer()
        self.timer.start(round(1000 / cctx.FPS), QtCore.Qt.PreciseTimer, self)

    def timerEvent(self, event):
        index = next(self.index)
        index = animation_index_to_data_index(index, self.data) or 0
        image = self.images[index + self.data['start_at_image']]
        self.animation_viewer.image = image

        for i, trigger in self.data['triggers'] or []:
            if i == index:
                self.animation_viewer.trigger = trigger
                break
        else:
            self.animation_viewer.trigger = None

        offsets = self.data['frames_centers']
        self.animation_viewer.offset = offsets[index] if offsets else None
        self.animation_viewer.hitmap = None
        self.animation_viewer.repaint()

        if self.prev_index == index:
            return

        self.prev_index = index
        for t, sound in self.triggers_sound_checked():
            if self.animation_viewer.trigger == t:
                print(self.animation_viewer.trigger)
                sound.play()

    def triggers_sound_checked(self):
        return [
            (it.trigger, it.sound) for it in self.items
            if it.checkState() == QtCore.Qt.Checked]


class ColorDialog(QtWidgets.QDialog):
    def __init__(self, color, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Select Color")
        self.color_wheel = ColorWheel()
        self.color_wheel.set_rgb255(*color)
        self.ok = QtWidgets.QPushButton("Ok")
        self.ok.released.connect(self.accept)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.color_wheel)
        self.layout.addWidget(self.ok)

    @property
    def rgb(self):
        return self.color_wheel.rgb255()


class SearchFileDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        flags = (
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint)
        super().__init__(parent, flags)
        excluded_extentions = ['png', 'wav', 'ogg']
        files = list_all_project_files(excluded_extentions)
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(files)
        self.combo.currentIndexChanged.connect(self.force_accept)
        self.completer = QtWidgets.QCompleter(files)
        self.combo.setEditable(True)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.combo.setCompleter(self.completer)
        self.combo.lineEdit().selectAll()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.combo)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            return self.accept()
        elif event.key() == QtCore.Qt.Key_Escape:
            return self.reject()

    def force_accept(self, *_):
        return self.accept()