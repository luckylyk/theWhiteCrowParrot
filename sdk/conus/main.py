import colorsys
from PySide6 import QtWidgets, QtCore, QtGui
from conus.palette import PaletteView, PaletteModel, PaletteScrollArea
from conus.slider import MultiValueSlider
from conus.imgutils import list_rgb_colors, switch_colors
from conus.coraxutils import scene_to_display_image, list_all_scenes
from PIL import ImageQt


R = {
    "bordercolor": "#591111",
    "backgroundcolor": "#554433",
    "linecolor": "yellow"}

G = {
    "bordercolor": "#115911",
    "backgroundcolor": "#335544",
    "linecolor": "yellow"}

B = {
    "bordercolor": "#111159",
    "backgroundcolor": "#334455",
    "linecolor": "yellow"}

H = {
    "bordercolor": "purple",
    "backgroundcolor": "#554433",
    "linecolor": "yellow"}

S = {
    "bordercolor": "darkGray",
    "backgroundcolor": "gray",
    "linecolor": "yellow"}

V = {
    "bordercolor": "gray",
    "backgroundcolor": "lightGray",
    "linecolor": "yellow"}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Conus')
        sides = QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.subWindowActivated.connect(self.sub_window_changed)

        self.palette = PaletteView()
        self.palette.selectionChanged.connect(self.colors_selected)
        self.palette.groupCreated.connect(self.change_colors)
        self.palette.sizeHint = lambda: QtCore.QSize(400, 400)
        self.palette_scroll = PaletteScrollArea(self.palette)
        self.palette_dock = QtWidgets.QDockWidget('Palette', self)
        self.palette_dock.setAllowedAreas(sides)
        self.palette_dock.setWidget(self.palette_scroll)

        self.scenelist = SceneList()
        self.scenelist.openScene.connect(self.add_scene)
        self.scenelist_dock = QtWidgets.QDockWidget('Scenes')
        self.scenelist_dock.setAllowedAreas(sides)
        self.scenelist_dock.setWidget(self.scenelist)

        self.colorshifter = ColorShifter()
        self.colorshifter.valuesChanged.connect(self.change_colors)
        self.colorshifter_dock = QtWidgets.QDockWidget('Color shift', self)
        self.colorshifter_dock.setAllowedAreas(sides)
        self.colorshifter_dock.setWidget(self.colorshifter)

        self.setCentralWidget(self.mdi_area)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.palette_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.colorshifter_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.scenelist_dock)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)
        self.palette.keyReleaseEvent(event)

    def colors_selected(self):
        self.colorshifter.set_colors(self.palette.selected_colors)

    def add_scene(self, filename):
        display_image = scene_to_display_image(filename)
        palette_model = PaletteModel()
        colors = list_rgb_colors(display_image)
        palette_model.colors = colors
        model = Model()
        model.image = display_image.copy()
        model.display_image = display_image
        model.palette_model = palette_model
        model.original_palette = colors.copy()
        widget = ImageLabel(model, self)
        self.palette.set_model(model.palette_model)
        self.mdi_area.addSubWindow(widget).show()

    def sub_window_changed(self, window):
        if not window:
            self.palette.set_model(PaletteModel())
            return
        self.palette.set_model(window.widget().model.palette_model)
        self.colors_selected()

    def change_colors(self):
        self.palette.set_selected_colors(self.colorshifter.colors)
        self.model.display_image = switch_colors(
            self.model.image,
            self.model.original_palette,
            self.palette.colors())
        self.mdi_area.currentSubWindow().widget().update_pixmap()

    @property
    def model(self):
        return self.mdi_area.currentSubWindow().widget().model


class ColorShifter(QtWidgets.QWidget):
    valuesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slider_r = MultiValueSlider(R)
        self.slider_r.valuesChanged.connect(self.change_rgb)
        self.slider_g = MultiValueSlider(G)
        self.slider_g.valuesChanged.connect(self.change_rgb)
        self.slider_b = MultiValueSlider(B)
        self.slider_b.valuesChanged.connect(self.change_rgb)
        self.slider_h = MultiValueSlider(H)
        self.slider_h.valuesChanged.connect(self.change_hsv)
        self.slider_s = MultiValueSlider(S)
        self.slider_s.valuesChanged.connect(self.change_hsv)
        self.slider_v = MultiValueSlider(V)
        self.slider_v.valuesChanged.connect(self.change_hsv)
        self.setFixedHeight(100)

        self.rgb_group = QtWidgets.QGroupBox('RGB')
        self.rgb_layout = QtWidgets.QVBoxLayout(self.rgb_group)
        self.rgb_layout.setSpacing(0)
        self.rgb_layout.setContentsMargins(0, 0, 0, 0)
        self.rgb_layout.setSpacing(0)
        self.rgb_layout.addWidget(self.slider_r)
        self.rgb_layout.addWidget(self.slider_g)
        self.rgb_layout.addWidget(self.slider_b)
        self.rgb_layout.addStretch(1)

        self.hsv_group = QtWidgets.QGroupBox('HSV')
        self.hsv_layout = QtWidgets.QVBoxLayout(self.hsv_group)
        self.hsv_layout.setSpacing(0)
        self.hsv_layout.setContentsMargins(0, 0, 0, 0)
        self.hsv_layout.setSpacing(0)
        self.hsv_layout.addWidget(self.slider_h)
        self.hsv_layout.addWidget(self.slider_s)
        self.hsv_layout.addWidget(self.slider_v)
        self.hsv_layout.addStretch(1)

        self.layer = QtWidgets.QHBoxLayout(self)
        self.layer.addWidget(self.rgb_group)
        self.layer.addWidget(self.hsv_group)

    def set_colors(self, colors):
        self.slider_r.set_values([color[0] for color in colors])
        self.slider_g.set_values([color[1] for color in colors])
        self.slider_b.set_values([color[2] for color in colors])
        hsv_colors = [colorsys.rgb_to_hsv(*c) for c in colors]
        self.slider_h.set_values([color[0] * 255 for color in hsv_colors])
        self.slider_s.set_values([color[1] * 255 for color in hsv_colors])
        self.slider_v.set_values([color[2] for color in hsv_colors])

    def change_rgb(self):
        hsv_colors = [colorsys.rgb_to_hsv(*c) for c in self.colors]
        self.slider_h.set_values([color[0] * 255 for color in hsv_colors])
        self.slider_s.set_values([color[1] * 255 for color in hsv_colors])
        self.slider_v.set_values([color[2] for color in hsv_colors])
        self.valuesChanged.emit()

    def change_hsv(self):
        h = [v / 255 for v in self.slider_h.values]
        s = [v / 255 for v in self.slider_s.values]
        hsv = list(zip(h, s, self.slider_v.values))
        colors = [colorsys.hsv_to_rgb(*c) for c in hsv]
        self.slider_r.set_values([color[0] for color in colors])
        self.slider_g.set_values([color[1] for color in colors])
        self.slider_b.set_values([color[2] for color in colors])
        self.valuesChanged.emit()

    @property
    def colors(self):
        r = self.slider_r.values
        g = self.slider_g.values
        b = self.slider_b.values
        return list(zip(r, g, b))


class SceneList(QtWidgets.QWidget):
    openScene = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list = QtWidgets.QListWidget()
        for name, filename in list_all_scenes():
            item = QtWidgets.QListWidgetItem(name)
            item.filename = filename
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(self.open_scene)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.list)

    def open_scene(self, item):
        self.openScene.emit(item.filename)


class ImageLabel(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(model.pixmap())
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.label)

    def update_pixmap(self):
        self.label.setPixmap(self.model.pixmap())


class Model:
    image = None
    display_image = None
    palette_model = None
    original_palette = None

    def pixmap(self):
        return QtGui.QPixmap.fromImage(ImageQt.ImageQt(self.display_image))

    def update_image(self):
        palette1 = self.original_palette
        palette2 = self.palette_model.colors
        self.display_image = switch_colors(self.image, palette1, palette2)
