import os
import traceback

from PySide6 import QtWidgets, QtCore, QtGui

import corax.context as cctx
from pluck.data import DEFAULT_MOVE
from pluck.field import (
    FieldPanel, LayersField, ColorField, StrField, IntVectorField)
from pluck.move import MoveDataEditor
from pluck.paint import PaintContext, render_image
from pluck.qtutils import sub_rects, build_spritesheet_image, spritesheet_to_images
from pluck.sanity import is_valid_animation_path


SHEET_OPTIOS_FIELDS = {
    "layers": LayersField,
    "key_color": ColorField,
    "frame_size": IntVectorField,
    "default_move": StrField
}


class SheetEditor(QtWidgets.QWidget):
    modified = QtCore.Signal()

    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        self.data = data
        self.move = None
        self.image = None
        self.images = []
        self.is_modified = False

        self.options = SheetOptions()
        self.options.edited.connect(self.options_edited)
        self.options.layersChanged.connect(self.set_layers)
        self.options.moveSelected.connect(self.set_move)
        self.options.moveCreated.connect(self.create_move)
        self.options.movesRemoved.connect(self.remove_moves)

        self.spritesheet = SpriteSheetView()
        self.spritesheet_scroll_area = QtWidgets.QScrollArea()
        self.spritesheet_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.spritesheet_scroll_area.setWidget(self.spritesheet)

        self.moveeditor = MoveDataEditor()
        self.moveeditor.edited.connect(self.move_edited)

        self.horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.horizontal_splitter.addWidget(self.spritesheet_scroll_area)
        self.horizontal_splitter.addWidget(self.moveeditor)
        self.vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vertical_splitter.addWidget(self.options)
        self.vertical_splitter.addWidget(self.horizontal_splitter)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.vertical_splitter)

        self.init_data()

    def sizeHint(self):
        return QtCore.QSize(250, 400)

    def init_data(self):
        self.options.values = self.data
        self.move = self.data["default_move"]
        self.options.select_move(self.move)
        self.set_layers(self.options.filenames)
        self.set_move(self.move)

    def set_move(self, move):
        if not self.data:
            return
        self.move = move
        data = self.data["moves"][move]
        self.moveeditor.values = data
        self.spritesheet.hightlight_move(move)

    def remove_moves(self, move_names):
        for move_name in move_names:
            del self.data['moves'][move_name]
        self.modified.emit()

    def create_move(self, move_name):
        self.data.update(self.options.values)
        self.data['moves'][move_name] = DEFAULT_MOVE.copy()
        self.set_move(move_name)
        self.modified.emit()

    def move_edited(self):
        if not self.move or not self.data:
            return
        self.data['moves'][self.move] = self.moveeditor.values
        self.spritesheet.hightlight_move(self.move)
        self.modified.emit()

    def options_edited(self, option):
        if not self.data or not self.move:
            return
        self.data.update(self.options.values)
        if option == 'frame_size':
            self.set_layers(self.options.filenames)
            self.spritesheet.hightlight_move(self.move)
        self.modified.emit()

    def set_layers(self, filenames):
        if not self.data or not self.move:
            return
        filenames = [os.path.join(cctx.ANIMATION_FOLDER, fn) for fn in filenames]
        filenames = [f for f in filenames if is_valid_animation_path(f)]
        self.image = build_spritesheet_image(filenames)
        self.images = spritesheet_to_images(self.image, self.data["frame_size"])
        self.spritesheet.set_image_data(image=self.image, data=self.data)
        self.moveeditor.set_images(self.images)
        self.repaint()


class SpriteSheetView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.data = None
        self.paintcontext = PaintContext()
        self.paintcontext.extra_zone = 0
        self.rects = []
        self.highlighted_rects = []
        self.setMouseTracking(True) # Necessary for wheelmouse event

    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def recompute_size(self):
        if not self.image:
            return
        w = self.paintcontext.relatives(self.image.width())
        h = self.paintcontext.relatives(self.image.height())
        self.setFixedSize(w, h)

    def set_image_data(self, image=None, data=None):
        self.image = image or self.image
        self.data = data or self.data
        if self.image and self.data:
            self.rects = sub_rects(self.image.rect(), self.data["frame_size"])
        self.recompute_size()

    def hightlight_move(self, move):
        if not self.data:
            return
        data = self.data["moves"][move]
        start = data["start_at_image"]
        end = start + len(data["frames_per_image"])
        self.highlighted_rects = self.rects[start:end]
        self.repaint()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.repaint()
        self.recompute_size()

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            if not self.image:
                return
            painter.begin(self)
            render_image(painter, self.image, 0, 0, self.paintcontext)
            for rect in self.highlighted_rects:
                painter.drawRect(self.paintcontext.relatives_rect(rect))
            painter.setPen(QtCore.Qt.black)
            rect = self.rect()
            rect.setHeight(rect.height() - 1)
            rect.setWidth(rect.width() - 1)
            painter.drawRect(rect)
            # Draw frame numbers
            for i, rect in enumerate(self.rects):
                rect = self.paintcontext.relatives_rect(rect)
                color = self.paintcontext.frame_number_color
                painter.setPen(QtGui.QPen(QtGui.QColor(color)))
                option = QtGui.QTextOption()
                align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom
                option.setAlignment(align)
                font = QtGui.QFont()
                font.setBold(True)
                font.setPixelSize(15)
                painter.setFont(font)
                painter.drawText(rect, str(i), option)
            painter.end()
        except Exception:
            print(traceback.format_exc())


class SheetOptions(QtWidgets.QWidget):
    edited = QtCore.Signal(str)
    moveSelected = QtCore.Signal(str)
    moveCreated = QtCore.Signal(str)
    movesRemoved = QtCore.Signal(list)
    layersChanged = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.options = FieldPanel(SHEET_OPTIOS_FIELDS)
        self.options.fieldEdited.connect(self.edited.emit)
        self.options.fields['layers'].stateChanged.connect(self.change_layers)
        self.options.fields['layers'].edited.connect(self.change_layers)

        self.move_selector = QtWidgets.QListWidget()
        self.move_selector.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.move_selector.dropEvent = self.reordered
        self.move_selector.itemSelectionChanged.connect(self.change_move)

        self.add = QtWidgets.QPushButton("Create animation")
        self.add.released.connect(self.create_animation)
        self.remove = QtWidgets.QPushButton("Remove animation(s)")
        self.remove.released.connect(self.remove_moves)
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_buttons.setContentsMargins(0, 0, 0, 0)
        self.layout_buttons.addWidget(self.add)
        self.layout_buttons.addWidget(self.remove)

        self.warning = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.options)
        self.layout.addWidget(self.move_selector)
        self.layout.addLayout(self.layout_buttons)
        self.layout.addWidget(self.warning)

    @property
    def filenames(self):
        return self.options.fields['layers'].filenames

    def change_layers(self):
        self.layersChanged.emit(self.options.fields['layers'].filenames)

    def reordered(self, event):
        QtWidgets.QListWidget.dropEvent(self.move_selector, event)
        event.acceptProposedAction()
        self.edited.emit()

    @property
    def values(self):
        values = self.options.values
        values['evaluation_order'] = self.moves
        return values

    @values.setter
    def values(self, values):
        self.options.values = values
        self.move_selector.clear()
        self.move_selector.addItems([m for m in values['evaluation_order']])

    @property
    def moves(self):
        return [
            self.move_selector.item(i).text()
            for i in range(self.move_selector.count())]

    @property
    def selected_moves(self):
        items = self.move_selector.selectedItems()
        if not items:
            return
        return [item.text() for item in items]

    def select_move(self, move):
        self.blockSignals(True)
        for i in range(self.move_selector.count()):
            item = self.move_selector.item(i)
            item.setSelected(item.text() == move)
        self.blockSignals(False)

    def remove_moves(self):
        indexes = self.move_selector.selectedIndexes()
        if not indexes:
            return
        names = [self.move_selector.item(i).text() for i in indexes]
        for index in indexes:
            self.move_selector.takeItem(index)
        self.movesRemoved.emit(names)

    def change_move(self):
        moves = self.selected_moves
        if moves:
            self.moveSelected.emit(moves[0])

    def create_animation(self):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Create a movement")
        dialog.setLabelText("Name")
        dialog.setTextValue("New_move")
        result = dialog.exec()
        if result != QtWidgets.QDialog.Accepted:
            return
        name = dialog.textValue()
        i = 0
        while name in self.moves:
            name = dialog.textValue() + "_{}".format(str(i).zfill(3))
            i += 1
        self.move_selector.addItem(name)
        self.moveCreated.emit(name)

    def validate(self):
        self.warning.setStyleSheet("")
        self.warning.setText("")

    def invalidate(self, exception):
        self.warning.setText(str(exception))
        self.warning.setStyleSheet("background-color:red")