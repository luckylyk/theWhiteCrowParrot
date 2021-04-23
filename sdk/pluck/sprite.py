import traceback
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from PyQt5 import QtCore, QtWidgets, QtGui
import corax.context as cctx
from corax.animation import build_images_list, build_centers_list
from pluck.paint import render_grid, render_image, PaintContext
from pluck.slider import Slider
from pluck.qtutils import sub_rects, spritesheet_to_images
from pluck.datas import data_to_plain_text, data_sanity_check, DEFAULT_MOVE
from pluck.highlighter import get_plaint_text_editor


class AnimationDataEditor(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent)
        path = os.path.join(cctx.ANIMATION_FOLDER, data["filename"])
        image = QtGui.QImage(path)

        self.data = data
        self.move = None
        self.options = Options()
        self.options.set_data(data)

        self.move_selector = QtWidgets.QListWidget()
        self.move_selector.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.move_selector.dropEvent = self.reordered
        self.move_selector.addItems(data["evaluation_order"])
        self.move_selector.itemSelectionChanged.connect(self.change_move)

        self.add = QtWidgets.QPushButton("Create animation")
        self.add.released.connect(self.create_animation)
        self.remove = QtWidgets.QPushButton("Remove animation")
        self.remove.released.connect(self.remove_animation)
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_buttons.setContentsMargins(0, 0, 0, 0)
        self.layout_buttons.addWidget(self.add)
        self.layout_buttons.addWidget(self.remove)

        self.move_editor, self.highlighter = get_plaint_text_editor("json")
        self.move_editor.textChanged.connect(self.data_edited)

        self.data_traceback = QtWidgets.QLabel()
        self.images = spritesheet_to_images(path, data["frame_size"])
        pc = PaintContext(data)
        pc.extra_zone = 0

        self.spritesheet_view = SpriteSheetView(image, data, pc)
        self.spritesheet_scroll_area = QtWidgets.QScrollArea()
        self.spritesheet_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.spritesheet_scroll_area.setWidget(self.spritesheet_view)

        move_data = data["moves"][data["default_move"]]
        images = build_images_list(move_data, self.images)
        centers = build_centers_list(move_data, data["frame_size"], flip=False)
        pc = PaintContext(data)
        pc.extra_zone = 0
        self.animation = AnimationReader(
            data["frame_size"], (0, 255, 0), images, centers, paintcontext=pc)

        self.result, self.result_highliter = get_plaint_text_editor("json")
        self.result.setReadOnly(True)
        self.result.setPlainText(data_to_plain_text(data))

        self.move_options = QtWidgets.QWidget()
        self.move_options_layout = QtWidgets.QVBoxLayout(self.move_options)
        self.move_options_layout.setContentsMargins(0, 0, 0, 0)
        self.move_options_layout.addWidget(self.options)
        self.move_options_layout.addWidget(self.move_selector)
        self.move_options_layout.addLayout(self.layout_buttons)

        self.move_widget = QtWidgets.QWidget()
        self.move_layout = QtWidgets.QVBoxLayout(self.move_widget)
        self.move_layout.setContentsMargins(0, 0, 0, 0)
        self.move_layout.addWidget(self.move_editor)
        self.move_layout.addWidget(self.data_traceback)

        self.left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.left_splitter.addWidget(self.move_options)
        self.left_splitter.addWidget(self.move_widget)
        self.right_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.right_splitter.addWidget(self.spritesheet_scroll_area)
        self.right_splitter.addWidget(self.animation)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.left_splitter)
        self.splitter.addWidget(self.right_splitter)
        self.splitter.addWidget(self.result)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.splitter)

    def change_move(self):
        items = self.move_selector.selectedItems()
        if not items:
            return
        self.move = items[0].text()
        move_data = self.data["moves"][self.move]
        images = build_images_list(move_data, self.images)
        centers = build_centers_list(move_data, self.data["frame_size"], flip=False)
        self.animation.set_data(images, centers)
        self.spritesheet_view.hightlight_move(self.move)
        self.move_editor.setPlainText(data_to_plain_text(move_data))

    def reordered(self, event):
        QtWidgets.QListWidget.dropEvent(self.move_selector, event)
        self.data["evaluation_order"] = [
            self.move_selector.item(i).text()
            for i in range(self.move_selector.count())]
        event.acceptProposedAction()
        self.result.setPlainText(data_to_plain_text(self.data))

    def remove_animation(self):
        items = self.move_selector.selectedItems()
        if not items:
            return
        self.move = None
        move = items[0].text()
        self.data["evaluation_order"].remove(move)

        del self.data["moves"][move]
        self.move_selector.takeItem(self.move_selector.currentRow())
        self.result.setPlainText(data_to_plain_text(self.data))

    def create_animation(self):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Create a movement")
        dialog.setLabelText("Name")
        dialog.setTextValue("New_move")
        result = dialog.exec_()
        if result != QtWidgets.QDialog.Accepted:
            return
        name = dialog.textValue()
        i = 0
        while name in self.data["moves"]:
            name = dialog.textValue() + "_{}".format(str(i).zfill(3))
            i += 1
        self.data["evaluation_order"].append(name)
        move = DEFAULT_MOVE.copy()
        self.data["moves"][name] = move
        self.move_selector.addItem(name)
        self.result.setPlainText(data_to_plain_text(self.data))

    def data_edited(self):
        if not self.move_editor.hasFocus():
            return
        text = self.move_editor.toPlainText()
        try:
            data = json.loads(text)
            data_sanity_check(data, "move")
        except json.decoder.JSONDecodeError:

            self.data_traceback.setText("JSon Syntax error")
            self.data_traceback.setStyleSheet("background-color:red")
            return
        except Exception as e:
            self.data_traceback.setText(str(e))
            self.data_traceback.setStyleSheet("background-color:red")
            return

        self.data_traceback.setText("")
        self.data_traceback.setStyleSheet("")
        self.data["moves"][self.move].update(data)
        self.spritesheet_view.hightlight_move(self.move)
        self.result.setPlainText(data_to_plain_text(self.data))


class SpriteSheetView(QtWidgets.QWidget):
    def __init__(self, image, data, paintcontext, parent=None):
        super().__init__(parent)
        self.image = image
        self.data = data
        self.paintcontext = paintcontext
        self.rects = sub_rects(image.rect(), data["frame_size"])
        self.hrects = []
        self.setMouseTracking(True)
        self.recompute_size()

    def hightlight_move(self, move):
        data = self.data["moves"][move]
        start = data["start_at_image"]
        end = start + len(data["frames_per_image"])
        self.hrects = self.rects[start:end]
        self.repaint()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.repaint()
        self.recompute_size()

    def recompute_size(self):
        w = self.paintcontext.relatives(self.image.width())
        h = self.paintcontext.relatives(self.image.height())
        self.setFixedSize(w, h)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        try:
            painter.begin(self)
            render_image(painter, self.image, 0, 0, self.paintcontext)
            for rect in self.hrects:
                painter.drawRect(self.paintcontext.relatives_rect(rect))
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


class AnimationReader(QtWidgets.QWidget):
    def __init__(
            self,
            size,
            background_color,
            images,
            centers,
            paintcontext=None,
            parent=None):
        super().__init__(parent)
        self.animation_image_viewer = AnimationImageViewer(
            size, background_color, images, centers, paintcontext)
        self.animation_scroll_area = QtWidgets.QScrollArea()
        self.animation_scroll_area.setWidget(self.animation_image_viewer)
        self.animation_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.slider = Slider()
        self.slider.minimum = 0
        self.slider.maximum = len(images) - 1
        self.slider.maximum_settable_value = len(images) - 1
        self.slider.valueChanged.connect(self.animation_image_viewer.set_index)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.animation_scroll_area)
        self.layout.addWidget(self.slider)

    def set_data(self, images, centers):
        self.animation_image_viewer.index = 0
        self.animation_image_viewer.images = images
        self.animation_image_viewer.centers = centers
        self.slider.value = 0
        self.slider.maximum_settable_value = len(images)
        self.slider.maximum = len(images)
        self.repaint()


class AnimationImageViewer(QtWidgets.QWidget):
    def __init__(
            self,
            size,
            background_color,
            images,
            centers,
            paintcontext=None,
            parent=None):
        super().__init__(parent)
        self.paintcontext = paintcontext
        self.images = images
        self.centers = centers
        self.size = size
        self.backgound_color = background_color
        self.setMouseTracking(True)
        self.index = 0
        self.recompute_size()

    def set_index(self, index):
        self.index = index
        self.repaint()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.paintcontext.zoomin()
        else:
            self.paintcontext.zoomout()
        self.repaint()
        self.recompute_size()

    def recompute_size(self):
        if self.paintcontext.zoom < 1:
            self.setFixedSize(*self.size)
        x = self.paintcontext.relatives(self.size[0])
        y = self.paintcontext.relatives(self.size[1])
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
        render_image(painter, self.images[self.index], 0, 0, self.paintcontext)
        center = self.centers[self.index]
        x = self.paintcontext.relatives(center[0])
        y = self.paintcontext.relatives(center[1])
        point = QtCore.QPointF(x, y)
        painter.drawEllipse(point, 2, 2)
        render_grid(
            painter,
            self.rect(),
            cctx.BLOCK_SIZE,
            paintcontext=self.paintcontext)


class Options(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None
        self.filename = QtWidgets.QLineEdit()
        self.key_color = QtWidgets.QLineEdit()
        self.frame_size = QtWidgets.QLineEdit()
        self.default_move = QtWidgets.QLineEdit()
        self.filename.textEdited.connect(self.validate)
        self.key_color.textEdited.connect(self.validate)
        self.frame_size.textEdited.connect(self.validate)
        self.default_move.textEdited.connect(self.validate)

        self.layout = QtWidgets.QFormLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addRow("Filename", self.filename)
        self.layout.addRow("Key color", self.key_color)
        self.layout.addRow("Frame size", self.frame_size)
        self.layout.addRow("Default move", self.default_move)

    def set_data(self, data):
        self.data = data
        self.filename.setText(data["filename"])
        self.key_color.setText(", ".join(str(n) for n in data["key_color"]))
        self.frame_size.setText(", ".join(str(n) for n in data["frame_size"]))
        self.default_move.setText(data["default_move"])
        self.validate()

    def validate(self):
        if self.data is None:
            return

        result = True
        filename = self.filename.text()

        if not os.path.exists(os.path.join(cctx.ANIMATION_FOLDER, filename)):
            result = False
            self.filename.setStyleSheet("background-color:red")
        else:
            self.filename.setStyleSheet("")

        try:
            key_color = [int(n) for n in self.key_color.text().split(",")]
            if len(key_color) != 3:
                raise ValueError()
            self.key_color.setStyleSheet("")
        except:
            result = False
            self.key_color.setStyleSheet("background-color:red")

        try:
            frame_size = [int(n) for n in self.frame_size.text().split(",")]
            if len(frame_size) != 2:
                raise ValueError()
            self.frame_size.setStyleSheet("")
        except:
            result = False
            self.frame_size.setStyleSheet("background-color:red")

        default_move = self.default_move.text()
        if default_move not in self.data["moves"]:
            result = False
            self.default_move.setStyleSheet("background-color:red")
        else:
            self.default_move.setStyleSheet("")

        if result:
            self.data["filename"] = filename
            self.data["key_color"] = key_color
            self.data["frame_size"] = frame_size
            self.data["default_move"] = default_move




if __name__ == "__main__":
    path = os.path.join(cctx.SHEET_FOLDER, "whitecrowparrot_chest.json")
    with open(path) as f:
        data = json.load(f)
    app = QtWidgets.QApplication([])
    win = AnimationDataEditor(data)
    win.show()
    app.exec()

