import itertools
import math
from PySide6 import QtWidgets, QtGui, QtCore
from conus.qtutils import shift_pressed, ctrl_pressed


class PaletteModel:
    def __init__(self):
        self.colors = []
        self.groups = []
        self.current_index = None
        self.selection = []

    def column_count(self, view_width, rect_width):
        count = 0
        larging = 0
        while (larging) < view_width:
            larging += rect_width
            count += 1
        count = (count - 1)
        return count

    def row_count(self, view_width, rect_width):
        rows = len(self.colors) / self.column_count(view_width, rect_width)
        return int(math.ceil(rows))

    def index(self, x, y, view_width, rect_width):
        count = self.column_count(view_width, rect_width)
        x -= (view_width % rect_width) / 2
        column = x // rect_width
        row = y // rect_width
        index = int(count * row + column)
        return index if index < len(self.colors) else None

    def group(self, index):
        for set_ in self.groups:
            if index in set_:
                return set_

    def create_group(self, indexes):
        for set_, index in itertools.product(self.groups, indexes):
            if index in set_:
                set_.remove(index)
        self.groups.append(set(indexes))
        color = self.colors[self.current_index]
        for index in indexes:
            self.colors[index] = color
        self.groups = [group for group in self.groups if group]

    def set_selection_colors(self, colors):
        if len(colors) != len(self.selection):
            m = 'Colors to set does not correspond to selection length'
            raise ValueError(m)

        for i, color in zip(self.selection, colors):
            self.colors[i] = color
            group = self.group(i)
            if group:
                for j in group:
                    self.colors[j] = color


class PaletteView(QtWidgets.QWidget):
    selectionChanged = QtCore.Signal()
    groupCreated = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = PaletteModel()
        self._rect_size = 25
        self._space_size = 3
        self._left_button = False

    def set_model(self, model):
        self._model = model
        self.compute_height()
        self.repaint()

    @property
    def rect_size(self):
        return self._rect_size

    @rect_size.setter
    def rect_size(self, value):
        self._rect_size = value
        self.repaint()

    @property
    def item_width(self):
        return self._rect_size + self._space_size

    @property
    def selected_colors(self):
        if not self._model.selection:
            return []
        return [self._model.colors[i] for i in self._model.selection]

    def set_selected_colors(self, colors):
        self._model.set_selection_colors(colors)
        self.repaint()

    def index(self, position):
        x, y = position.x(), position.y()
        return self._model.index(x, y, self.width(), self.item_width)

    def _change_color(self, event):
        self._model.selection = [self.index(event.position())]
        self.repaint()
        current_color = self.current_color()
        if current_color is not None:
            self.currentColorChanged.emit(self.current_color())

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return and self._model.selection:
            self._model.create_group(self._model.selection)
            self.groupCreated.emit()
            self.repaint()
        if event.key() == QtCore.Qt.Key_Plus and self._rect_size < 150:
            self.set_rectangles_sizes(self._rect_size + 2)
            self.repaint()
        if event.key() == QtCore.Qt.Key_Minus and self._rect_size > 5:
            self.set_rectangles_sizes(self._rect_size - 2)
            self.repaint()

    def resizeEvent(self, _):
        self.compute_height()

    def compute_height(self):
        row = self._model.row_count(self.width(), self.item_width)
        self.setFixedHeight(row * self.item_width)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._left_button = True

    def mouseMoveEvent(self, event):
        if not self._left_button:
            return

        if shift_pressed() and not ctrl_pressed():
            hovered_index = self.index(event.position())
            if hovered_index and hovered_index not in self._model.selection:
                self._model.selection.append(hovered_index)
                self._model.current_index = hovered_index
                self._model.selection.sort()
                self.selectionChanged.emit()
                self.repaint()

    def mouseReleaseEvent(self, event):
        if event.button() != QtCore.Qt.LeftButton:
            return
        self._left_button = False

        clicked_index = self.index(event.position())
        if not (shift_pressed() or ctrl_pressed()):
            self._model.selection = [clicked_index] if clicked_index else []

        elif not shift_pressed() and ctrl_pressed() and clicked_index:
            self._model.selection.append(clicked_index)
            self._model.selection.sort()

        elif shift_pressed() and not ctrl_pressed() and clicked_index:
            if self._model.current_index is None:
                self._model.selection = [clicked_index]
            else:
                start = min([self._model.current_index, clicked_index])
                end = max([self._model.current_index, clicked_index])
                selection = range(start, end + 1)
                self._model.selection.extend(selection)
                self._model.selection = sorted(list(set(self._model.selection)))

        elif shift_pressed() and ctrl_pressed() and clicked_index in self._model.selection:
            self._model.selection.remove(clicked_index)

        self.selectionChanged.emit()
        self._model.current_index = clicked_index
        self.repaint()

    def paintEvent(self, _):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.paint(painter)
        painter.end()

    def paint(self, painter):
        rect_width = self._rect_size + self._space_size
        shift = (self.width() % rect_width) / 2
        left, top = shift, 0
        pen = QtGui.QPen()
        group = self._model.group(self._model.current_index)
        for index, color in enumerate(self._model.colors):
            if index == self._model.current_index:
                pen.setWidth(3)
                pen.setColor(QtGui.QColor('yellow'))
            elif index in self._model.selection:
                pen.setWidth(2)
                pen.setColor(QtGui.QColor('red'))
            else:
                pen.setWidth(1)
                pen.setColor(QtGui.QColor('#000000'))

            painter.setPen(pen)
            painter.setBrush(QtGui.QColor(*color))
            painter.drawRect(left, top, self._rect_size, self._rect_size)
            count = self._model.column_count(self.width(), rect_width)
            if group and index in group and index != self._model.current_index:
                brush = QtGui.QBrush(QtCore.Qt.yellow)
                brush.setStyle(QtCore.Qt.FDiagPattern)
                painter.setBrush(brush)
                painter.setPen(QtCore.Qt.transparent)
                painter.drawRect(left, top, self._rect_size, self._rect_size)
            left += rect_width
            if (index + 1) % count == 0:
                left = shift
                top += rect_width

    def current_color(self):
        if not self._model.selection:
            return
        if len(self._model.colors) > max(self._model.selection):
            return self._model.colors[self._model.selection[-1]]

    def set_colors(self, colors):
        self._model.colors = colors
        self.repaint()

    def colors(self):
        return self._model.colors


class PaletteScrollArea(QtWidgets.QScrollArea):
    def __init__(self, palette, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setWidget(palette)

    def resizeEvent(self, event):
        width = event.size().width() # - self.verticalScrollBar().width()
        self.widget().setFixedWidth(width)
