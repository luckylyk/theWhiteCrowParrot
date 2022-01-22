import traceback

from PySide6 import QtWidgets, QtCore, QtGui

import corax.context as cctx
from corax.animation import animation_index_to_data_index, data_index_to_animation_index
from pluck.arrayutils import match_arrays_length
from pluck.dialog import TriggerDialog, LineTestDialog
from pluck.field import (
    BoolField, IntVectorField, StrField, IntArrayField, IntField, DictField,
    StrArrayField, FieldPanel)
from pluck.parsing import list_all_existing_hitboxes
from pluck.qtutils import get_icon
from pluck.paint import (
    render_image, render_grid, render_trigger, render_hitbox, render_center,
    PaintContext)
from pluck.slider import Slider


MOVE_OPTIONS_FIELDS = {
    "center": IntVectorField,
    "conditions": DictField,
    "frames_per_image": IntArrayField,
    "hold": BoolField,
    "inputs": StrArrayField,
    "loop_on":  StrField,
    "next_move": StrField,
    "next_move_bufferable": BoolField,
    "post_events": DictField,
    "pre_events": DictField,
    "release_frame": IntField,
    "start_at_image": IntField
}


class MoveDataEditor(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.data = None
        self.images = []

        self.options = FieldPanel(MOVE_OPTIONS_FIELDS)
        self.options.fieldEdited.connect(self.option_set)
        self.options.setFixedWidth(350)
        self.animation_editor = AnimationEditor()
        self.animation_editor.animation_viewer.mouseEdit.connect(self.mouse_edit)
        self.animation_editor.hbtoolbar.hitboxCreated.connect(self.create_hitbox)
        self.animation_editor.hbtoolbar.hitboxRemoved.connect(self.delete_hitbox)
        self.animation_editor.toolbar.clearHitbox.connect(self.clear_hitbox_frame)
        self.animation_editor.toolbar.addTriggerRequested.connect(self.add_trigger)
        self.animation_editor.toolbar.removeTriggerRequested.connect(self.remove_trigger)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.animation_editor)
        self.splitter.addWidget(self.options)

        self.layer = QtWidgets.QHBoxLayout(self)
        self.layer.setContentsMargins(0, 0, 0, 0)
        self.layer.addWidget(self.splitter)

    @property
    def values(self):
        values = self.options.values
        values.update(self.animation_editor.data)
        return values

    @values.setter
    def values(self, values):
        self.options.values = values
        self.data = values
        self.animation_editor.set_data_images(data=values)
        name = list(values['hitboxes'].keys())[0] if values['hitboxes'] else None
        self.animation_editor.change_hitbox(name)
        self.repaint()

    def option_set(self, option):
        if not self.data:
            return
        if option == "frames_per_image" and self.data['frames_centers']:
            durations = self.options.values[option]
            self.data['frames_centers'] = match_arrays_length(
                self.data['frames_centers'], durations, default=[0, 0])
            for hitbox_name in self.data['hitboxes']:
                self.data['hitboxes'][hitbox_name] = match_arrays_length(
                    self.data['hitboxes'][hitbox_name], durations, default=[])

        self.data.update({option: self.options.values[option]})
        self.edited.emit()

    def set_images(self, images):
        self.images = images
        self.animation_editor.set_data_images(images=images)
        self.repaint()

    def mouse_edit(self, pixel_position, block_position):
        match self.animation_editor.toolbar.mode:
            case "paint":
                hitbox_name = self.animation_editor.hitbox_name
                self.paint_block(hitbox_name, *block_position)
            case "erase":
                hitbox_name = self.animation_editor.hitbox_name
                self.erase_block(hitbox_name, *block_position)
            case "center":
                self.edit_center(*pixel_position)
            case "offset":
                self.edit_offset(*pixel_position)

    def create_hitbox(self, name):
        conditions = (
            self.data is None or
            name in (self.data["hitboxes"] or {}))

        if conditions:
            return

        if self.data["hitboxes"] is None:
            self.data["hitboxes"] = {}

        frames = len(self.data["frames_per_image"])
        self.data["hitboxes"][name] = [[] for _ in range(frames)]
        self.edited.emit()

    def delete_hitbox(self, name):
        if not self.data or name not in self.data["hitboxes"]:
            return
        del self.data["hitboxes"][name]
        self.edited.emit()

    def clear_hitbox_frame(self):
        name = self.animation_editor.hitbox_name
        if not self.data or not name:
            return

        if self.animation_editor.toolbar.range_mode == 'single':
            index = self.animation_editor.data_index
            hitbox = self.data["hitboxes"][name][index]
            hitbox.clear()
        else:
            for hitbox in self.data["hitboxes"][name]:
                hitbox.clear()
        self.edited.emit()

    def hitboxes_to_edit(self, name):
        if self.animation_editor.toolbar.range_mode != 'single':
            return [self.data["hitboxes"].get(name)]
        index = self.animation_editor.data_index
        return [self.data["hitboxes"][name][index]]

    def paint_block(self, name, x, y):
        if not self.data or not name:
            return
        for hitbox in self.hitboxes_to_edit(name):
            # Skip if block already in the hitbox
            for block in hitbox:
                if block[0] == x and block[1] == y:
                    break
            else:
                hitbox.append([x, y])
        self.animation_editor.set_data_images(data=self.data)
        self.edited.emit()

    def erase_block(self, name, x, y):
        if not self.data or not name:
            return
        for hitbox in self.hitboxes_to_edit(name):
            for block in hitbox:
                if block[0] == x and block[1] == y:
                    hitbox.remove(block)
        self.animation_editor.set_data_images(data=self.data)
        self.edited.emit()

    def edit_center(self, x, y):
        if not self.data:
            return
        self.data['center'] = [x, y]
        self.animation_editor.set_data_images(data=self.data)
        self.edited.emit()

    def edit_offset(self, x, y):
        if not self.data:
            return
        x -= self.data['center'][0]
        y -= self.data['center'][1]
        index = self.animation_editor.data_index
        if not self.data['frames_centers']:
            length = len(self.data['frames_per_image'])
            self.data['frames_centers'] = [[0, 0] for _ in range(length)]
        self.data['frames_centers'][index] = [x, y]
        self.animation_editor.set_data_images(data=self.data)
        self.edited.emit()

    def add_trigger(self):
        if not self.data:
            return

        dialog = TriggerDialog()
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return

        index = self.animation_editor.data_index
        trigger = [index, dialog.trigger]

        # If it is the first trigger set on the move.
        if not self.data["triggers"]:
            self.data["triggers"] = [trigger]
            self.edited.emit()
            self.animation_editor.set_data_images(data=self.data)
            return

        # Skip if already existing.
        for existing_trigger in self.data["triggers"]:
            conditions = (
                trigger[0] == existing_trigger[0] and
                trigger[1] and existing_trigger[1])
            if conditions:
                return

        self.data["triggers"].append(trigger)
        self.data["triggers"].sort(key=lambda x: x[0])
        self.animation_editor.set_data_images(data=self.data)
        self.edited.emit()

    def remove_trigger(self):
        if not self.data:
            return
        index = self.animation_editor.data_index
        for trigger in self.data["triggers"]:
            if index == trigger[0]:
                self.data["triggers"].remove(trigger)
                self.animation_editor.set_data_images(data=self.data)
                self.edited.emit()
                return


class AnimationEditor(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = {}
        self.images = []
        self.hitbox_name = ""

        self.toolbar = AnimationToolbar()
        self.toolbar.lineTestRequested.connect(self.show_linetest)

        self.hbtoolbar = HitboxToolbar()
        self.hbtoolbar.hitboxChanged.connect(self.change_hitbox)

        self.animation_viewer = AnimationViewer()
        self.animation_scroll_area = QtWidgets.QScrollArea()
        self.animation_scroll_area.setWidget(self.animation_viewer)
        self.animation_scroll_area.setAlignment(QtCore.Qt.AlignCenter)

        self.slider = Slider()
        self.slider.minimum = 0
        self.slider.valueChanged.connect(self.set_index)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.hbtoolbar)
        self.layout.addWidget(self.animation_scroll_area)
        self.layout.addWidget(self.slider)

    def set_data_images(self, data=None, images=None):
        if images is not None:
            self.images = images
        if data is not None:
            self.data = data
            self.animation_viewer.center = data['center']
            self.slider.maximum = sum(data['frames_per_image'])
            self.slider.marks = [
                data_index_to_animation_index(i, data)
                for i, _ in data['triggers'] or []]
            names = data['hitboxes'].keys() if data['hitboxes'] else None
            self.hbtoolbar.set_hitbox_names(names)
        self.set_index(self.slider.value)

    @property
    def data_index(self):
        index = self.slider.value
        return animation_index_to_data_index(index, self.data)

    def set_index(self, index):
        if not self.data:
            return
        index = animation_index_to_data_index(index, self.data) or 0
        if self.images:
            image = self.images[index + self.data['start_at_image']]
        else:
            image = None
        self.animation_viewer.image = image
        offsets = self.data['frames_centers']
        self.animation_viewer.offset = offsets[index] if offsets else None
        self.animation_viewer.trigger = self.trigger_for_index(index)
        self.animation_viewer.hitbox = self.hitbox(self.hitbox_name, index)
        self.animation_viewer.recompute_size()
        self.animation_viewer.repaint()

    def hitbox(self, name, index):
        hitboxes = self.data["hitboxes"]
        if not hitboxes:
            return
        sequence = hitboxes.get(name)
        if not sequence:
            return
        return sequence[index]

    def trigger_for_index(self, index):
        if not self.data['triggers']:
            return
        for i, trigger in self.data['triggers']:
            if i == index:
                return trigger

    def edit_current_frame(self):
        return self.toolbar.edit_current_frame()

    def change_hitbox(self, name):
        if name is None:
            self.animation_viewer.hitbox = None
            self.animation_viewer.repaint()
            return

        self.hitbox_name = name
        index = animation_index_to_data_index(self.slider.value, self.data)
        self.animation_viewer.hitbox = self.hitbox(name, index)
        self.animation_viewer.repaint()

    def show_linetest(self):
        dialog = LineTestDialog(self.data, self.images, AnimationViewer())
        dialog.exec()


class AnimationViewer(QtWidgets.QWidget):
    mouseEdit = QtCore.Signal(tuple, tuple)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paintcontext = PaintContext()
        self.paintcontext.extra_zone = 0
        self.is_clicked = False
        self.render_options = ['grid', 'center', 'hitbox', 'trigger']

        self._image = None
        self.center = (0, 0)
        self.offset = (0, 0)
        self.hitbox = None
        self.trigger = None
        self.backgound_color = cctx.KEY_COLOR
        self.size = None

        self.setMouseTracking(True)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        if self._image is None or self._image.size() != image.size():
            self._image = image
            self.recompute_size()
        self._image = image

    def mousePressEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return
        self.is_clicked = True
        self.emit_mouse_clicked(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return
        self.is_clicked = False

    def mouseMoveEvent(self, event):
        if self.is_clicked:
            self.emit_mouse_clicked(event.position())

    def emit_mouse_clicked(self, position):
        if not self.rect().contains(position.toPoint()):
            return
        pix_x = self.paintcontext.absolute(position.x())
        pix_y = self.paintcontext.absolute(position.y())
        block_x, block_y = self.paintcontext.block_position(position.x(), position.y())
        self.mouseEdit.emit((pix_x, pix_y), (block_x, block_y))

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.repaint()
        self.recompute_size()

    def recompute_size(self):
        if self._image is None:
            return
        self.size = self._image.size()
        if self.paintcontext.zoom < 1:
            self.setFixedSize(self.size)
        x = self.paintcontext.relatives(self.size.width())
        y = self.paintcontext.relatives(self.size.height())
        self.setFixedSize(x, y)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            self.paint(painter)
            painter.end()
        except Exception:
            print(traceback.format_exc())

    def paint(self, painter):
        if not all((self._image, self.center)):
            return
        render_image(painter, self._image, 0, 0, self.paintcontext)
        if 'grid' in self.render_options:
            render_grid(
                painter,
                self.rect(),
                cctx.BLOCK_SIZE,
                paintcontext=self.paintcontext)

        if 'center' in self.render_options:
            render_center(
                painter,
                self.center,
                self.offset,
                paintcontext=self.paintcontext)

        if 'hitbox' in self.render_options and self.hitbox:
            color = 255, 255, 255
            render_hitbox(
                painter,
                hitbox=self.hitbox,
                color=color,
                paintcontext=self.paintcontext)

        if 'trigger' in self.render_options and self.trigger:
            render_trigger(painter, self.trigger, self.rect(), self.paintcontext)


class HitboxToolbar(QtWidgets.QToolBar):
    hitboxCreated = QtCore.Signal(str)
    hitboxRemoved = QtCore.Signal(str)
    hitboxChanged = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hitbox_names = QtWidgets.QComboBox()
        self.hitbox_names.currentTextChanged.connect(self.change_hitbox)
        self.hitbox_names.setFixedWidth(200)
        self.add = QtGui.QAction("+", self)
        self.add.triggered.connect(self.add_requested)
        self.rmv = QtGui.QAction("-", self)
        self.rmv.triggered.connect(self.remove_requested)
        self.addWidget(QtWidgets.QLabel('Hitboxes:'))
        self.addWidget(self.hitbox_names)
        self.addAction(self.add)
        self.addAction(self.rmv)

    def set_hitbox_names(self, names):
        self.blockSignals(True)
        self.hitbox_names.clear()
        if names:
            self.hitbox_names.addItems(names)
        self.blockSignals(False)

    def add_requested(self):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Create hitbox")
        dialog.setLabelText("Enter a hitbox name")
        dialog.setTextValue("")
        le = dialog.findChild(QtWidgets.QLineEdit)
        words = list_all_existing_hitboxes()
        completer = QtWidgets.QCompleter(words, le)
        le.setCompleter(completer)
        result = dialog.exec()
        name = dialog.textValue()

        if result != QtWidgets.QDialog.Accepted or not name:
            return

        count = range(self.hitbox_names.count())
        names = [self.hitbox_names.itemText(i) for i in count]
        if name in names: # Name already exists
            self.hitbox_names.setCurrentText(name)
            return
        self.hitbox_names.addItem(name)
        self.hitboxCreated.emit(name)
        self.hitbox_names.setCurrentText(name)

    def remove_requested(self):
        name = self.hitbox_names.currentText()
        if not name:
            return
        self.hitboxRemoved.emit(name)
        count = range(self.hitbox_names.count())
        names = [self.hitbox_names.itemText(i) for i in count]
        self.hitbox_names.removeItem(names.index(name))

    def change_hitbox(self, _):
        self.hitboxChanged.emit(self.hitbox_name)

    @property
    def hitbox_name(self):
        return self.hitbox_names.currentText()


class AnimationToolbar(QtWidgets.QToolBar):
    addTriggerRequested = QtCore.Signal()
    removeTriggerRequested = QtCore.Signal()
    lineTestRequested = QtCore.Signal()
    clearHitbox = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setIconSize(QtCore.QSize(16, 16))
        self.linetest = QtGui.QAction(get_icon("play.png"), "", self)
        self.linetest.triggered.connect(self.lineTestRequested.emit)

        self.pointer = QtGui.QAction(get_icon("pointer.png"), "", self)
        self.pointer.setCheckable(True)
        self.pointer.setChecked(True)
        self.brush = QtGui.QAction(get_icon("brush.png"), "", self)
        self.brush.setCheckable(True)
        self.erase = QtGui.QAction(get_icon("eraser.png"), "", self)
        self.erase.setCheckable(True)
        self.clear = QtGui.QAction(get_icon("clear.png"), "", self)
        self.clear.triggered.connect(self.clear_requested)

        self.center = QtGui.QAction(get_icon("center.png"), "", self)
        self.center.setCheckable(True)
        self.offset = QtGui.QAction(get_icon("offset.png"), "", self)
        self.offset.setCheckable(True)

        self.action_group_1 = QtGui.QActionGroup(self)
        self.action_group_1.addAction(self.pointer)
        self.action_group_1.addAction(self.brush)
        self.action_group_1.addAction(self.erase)
        self.action_group_1.addAction(self.center)
        self.action_group_1.addAction(self.offset)

        self.unique = QtGui.QAction(get_icon("frame.png"), "", self)
        self.unique.setCheckable(True)
        self.unique.setChecked(True)
        self.frames = QtGui.QAction(get_icon("frames.png"), "", self)
        self.frames.setCheckable(True)

        self.add_trigger = QtGui.QAction(get_icon("trigger.png"), "", self)
        self.add_trigger.triggered.connect(self.addTriggerRequested.emit)
        self.remove_trigger = QtGui.QAction(get_icon("remove_trigger.png"), "", self)
        self.remove_trigger.triggered.connect(self.removeTriggerRequested.emit)

        self.action_group_2 = QtGui.QActionGroup(self)
        self.action_group_2.addAction(self.unique)
        self.action_group_2.addAction(self.frames)

        self.addAction(self.linetest)
        self.addSeparator()
        self.addAction(self.pointer)
        self.addAction(self.brush)
        self.addAction(self.erase)
        self.addAction(self.clear)
        self.addSeparator()
        self.addAction(self.center)
        self.addAction(self.offset)
        self.addSeparator()
        self.addAction(self.unique)
        self.addAction(self.frames)
        self.addSeparator()
        self.addAction(self.add_trigger)
        self.addAction(self.remove_trigger)

    @property
    def mode(self):
        if self.pointer.isChecked():
            return "point"
        elif self.brush.isChecked():
            return "paint"
        elif self.erase.isChecked():
            return "erase"
        elif self.center.isChecked():
            return "center"
        elif self.offset.isChecked():
            return "offset"

    @property
    def range_mode(self):
        return 'single' if self.unique.isChecked() else 'range'

    def edit_current_frame(self):
        return self.unique.isChecked()

    def clear_requested(self):
        self.clearHitbox.emit()