import colorsys
from functools import partial
from PIL import ImageQt
from PySide6 import QtWidgets, QtCore, QtGui

from conus.colorwheel import ColorWheel
from conus.coraxutils import (
    scene_to_display_image, list_all_scenes, list_all_sheets,
    load_sheet, sheet_to_image_display)
from conus.imagedisplay import ImageDisplay, AnimationDisplay
from conus.imgutils import list_rgb_colors, switch_colors, get_frame
from conus.multislider import MultiValueSlider
from conus.outliner import build_scene_tree
from conus.palette import PaletteView, PaletteModel, PaletteScrollArea


MDI_BACKGROUND_COLOR = '#101010'
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

        areas = (
            QtCore.Qt.LeftDockWidgetArea |
            QtCore.Qt.RightDockWidgetArea |
            QtCore.Qt.BottomDockWidgetArea)
        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.subWindowActivated.connect(self.sub_window_changed)
        color = QtGui.QColor(MDI_BACKGROUND_COLOR)
        self.mdi_area.setBackground(QtGui.QBrush(color))
        self.mdi_area.setTabsClosable(True)

        self.export = QtGui.QAction('Export', self)
        self.close_file = QtGui.QAction('Close', self)
        self.close_file.triggered.connect(self.mdi_area.closeActiveSubWindow)
        self.close_others = QtGui.QAction('Close Others', self)
        self.close_all = QtGui.QAction('Close All', self)
        self.close_all.triggered.connect(self.mdi_area.closeAllSubWindows)
        self.quit = QtGui.QAction('Quit', self)
        self.quit.triggered.connect(self.close)
        self.mosaic = QtGui.QAction('Mosaic', self)
        self.mosaic.triggered.connect(self.mdi_area.tileSubWindows)
        self.cascade = QtGui.QAction('Cascade', self)
        self.cascade.triggered.connect(self.mdi_area.cascadeSubWindows)
        self.floating = QtGui.QAction('Floating Documents', self)
        mode = QtWidgets.QMdiArea.SubWindowView
        mth = partial(self.mdi_area.setViewMode, mode)
        self.floating.triggered.connect(mth)
        self.tabbed = QtGui.QAction('Tabbed Documents', self)
        mth = partial(self.mdi_area.setViewMode, QtWidgets.QMdiArea.TabbedView)
        self.tabbed.triggered.connect(mth)
        self.about = QtGui.QAction('About', self)

        self.file = QtWidgets.QMenu('&File')
        self.file.addAction(self.export)
        self.file.addSeparator()
        self.file.addAction(self.close_file)
        self.file.addAction(self.close_others)
        self.file.addAction(self.close_all)
        self.file.addSeparator()
        self.file.addAction(self.quit)

        self.tools = QtWidgets.QMenu('&Tools')
        self.windows = QtWidgets.QMenu('&Windows')
        self.windows.addAction(self.mosaic)
        self.windows.addAction(self.cascade)
        self.windows.addSeparator()
        self.windows.addAction(self.floating)
        self.windows.addAction(self.tabbed)
        self.help = QtWidgets.QMenu('&Help')
        self.help.addAction(self.about)

        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.addMenu(self.file)
        self.menu_bar.addMenu(self.tools)
        self.menu_bar.addMenu(self.windows)
        self.menu_bar.addMenu(self.help)
        self.setMenuBar(self.menu_bar)

        self.setWindowTitle('Conus')
        self.setDockNestingEnabled(True)

        self.palette = PaletteView()
        self.palette.selectionChanged.connect(self.colors_selected)
        self.palette.groupCreated.connect(self.change_colors)
        self.palette.sizeHint = lambda: QtCore.QSize(400, 400)
        self.palette_scroll = PaletteScrollArea(self.palette)
        self.palette_dock = QtWidgets.QDockWidget('Palette', self)
        self.palette_dock.setAllowedAreas(areas)
        self.palette_dock.setWidget(self.palette_scroll)

        self.scenelist = SceneList()
        self.scenelist.openScene.connect(self.add_scene)
        self.sheetlist = SheetList()
        self.sheetlist.openScene.connect(self.add_sheet)
        self.assetlist = QtWidgets.QTabWidget()
        self.assetlist.addTab(self.scenelist, 'Scenes')
        self.assetlist.addTab(self.sheetlist, 'Sheets')
        self.assetlist_dock = QtWidgets.QDockWidget('Assets', self)
        self.assetlist_dock.setAllowedAreas(areas)
        self.assetlist_dock.setWidget(self.assetlist)

        self.outliner = QtWidgets.QTreeWidget()
        self.outliner.setHeaderHidden(True)
        self.outliner_dock = QtWidgets.QDockWidget('Layers', self)
        self.outliner_dock.setAllowedAreas(areas)
        self.outliner_dock.setWidget(self.outliner)

        self.colorwheel = ColorWheel()
        self.colorwheel.currentColorChanged.connect(self.change_color)
        self.colorwheel_dock = QtWidgets.QDockWidget('Color', self)
        self.colorwheel_dock.setAllowedAreas(areas)
        self.colorwheel_dock.setWidget(self.colorwheel)

        self.colorshifter = ColorShifter()
        self.colorshifter.valuesChanged.connect(self.change_colors)
        self.colorshifter_dock = QtWidgets.QDockWidget('Color shift', self)
        self.colorshifter_dock.setAllowedAreas(areas)
        self.colorshifter_dock.setWidget(self.colorshifter)

        self.setCentralWidget(self.mdi_area)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.palette_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.colorshifter_dock)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.colorwheel_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.assetlist_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.outliner_dock)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_F10:
            if self.windowState() == self.windowState() | QtCore.Qt.WindowFullScreen:
                self.setWindowState(QtCore.Qt.WindowNoState)
            else:
                self.setWindowState(QtCore.Qt.WindowFullScreen)
        elif event.key() == QtCore.Qt.Key_Tab:
            if self.assetlist_dock.isVisible():
                area = QtCore.Qt.BottomDockWidgetArea
                self.addDockWidget(area, self.palette_dock)
                self.addDockWidget(area, self.colorshifter_dock)
                self.addDockWidget(area, self.colorwheel_dock)
                self.assetlist_dock.hide()
                self.outliner_dock.hide()
            else:
                area = QtCore.Qt.LeftDockWidgetArea
                self.addDockWidget(area, self.palette_dock)
                self.addDockWidget(area, self.colorshifter_dock)
                self.addDockWidget(area, self.colorwheel_dock)
                self.assetlist_dock.show()
                self.outliner_dock.show()
        elif event.key() == QtCore.Qt.Key_A:
            if self.mdi_area.viewMode() == QtWidgets.QMdiArea.TabbedView:
                self.mdi_area.setViewMode(QtWidgets.QMdiArea.SubWindowView)
            else:
                self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.palette.keyReleaseEvent(event)

    def keyPressEvent(self, event):
        if self.current_widget:
            self.current_widget.keyPressEvent(event)

    def colors_selected(self):
        self.colorshifter.set_colors(self.palette.selected_colors)
        self.colorwheel.setEnabled(len(self.palette.selected_colors) == 1)
        if not self.palette.selected_colors:
            return
        self.colorwheel.set_rgb255(*self.palette.selected_colors[0])

    def add_scene(self, filename):
        display_image = scene_to_display_image(filename)
        palette_model = PaletteModel()
        colors = list_rgb_colors(display_image)
        palette_model.colors = colors
        model = SceneModel()
        model.image = display_image.copy()
        model.display_image = display_image
        model.palette_model = palette_model
        model.filename = filename
        model.original_palette = colors.copy()
        widget = ImageDisplay(model)
        self.palette.set_model(model.palette_model)
        window = self.mdi_area.addSubWindow(widget)
        window.setWindowTitle(filename)
        window.show()

    def add_sheet(self, filename):
        data = load_sheet(filename)
        layers = list(data['layers'])
        display_image = sheet_to_image_display(filename, layers)
        palette_model = PaletteModel()
        colors = list_rgb_colors(display_image)
        palette_model.colors = colors
        model = AnimationModel()
        model.data = data
        model.display_image = display_image
        model.palette_model = palette_model
        model.image = display_image.copy()
        model.filename = filename
        model.original_palette = colors.copy()
        widget = AnimationDisplay(model)
        self.palette.set_model(model.palette_model)
        window = self.mdi_area.addSubWindow(widget)
        window.setWindowTitle(filename)
        window.show()
        widget.reset()

    def sub_window_changed(self, window):
        if not window:
            self.palette.set_model(PaletteModel())
            return
        self.palette.set_model(window.widget().model.palette_model)
        self.outliner.clear()
        if isinstance(self.model, SceneList):
            for item in build_scene_tree(self.model.filename, self.outliner):
                self.outliner.addTopLevelItem(item)
        self.colors_selected()

    def change_colors(self):
        self.palette.set_selected_colors(self.colorshifter.colors)
        self.model.display_image = switch_colors(
            self.model.image,
            self.model.original_palette,
            self.palette.colors())
        self.current_widget.repaint()

    def change_color(self):
        self.palette.set_selected_colors([self.colorwheel.rgb255()])
        self.model.display_image = switch_colors(
            self.model.image,
            self.model.original_palette,
            self.palette.colors())
        self.current_widget.repaint()

    @property
    def current_widget(self):
        window = self.mdi_area.currentSubWindow()
        return window.widget() if window else None

    @property
    def model(self):
        window = self.mdi_area.currentSubWindow()
        return window.widget().model if window else None


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

        self.hlayer = QtWidgets.QHBoxLayout()
        self.hlayer.setContentsMargins(0, 0, 0, 0)
        self.hlayer.addWidget(self.rgb_group)
        self.hlayer.addWidget(self.hsv_group)

        self.layer = QtWidgets.QVBoxLayout(self)
        self.layer.addLayout(self.hlayer)
        self.layer.addStretch(1)

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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.list)

    def open_scene(self, item):
        self.openScene.emit(item.filename)


class SheetList(QtWidgets.QWidget):
    openScene = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list = QtWidgets.QListWidget()
        for filename in list_all_sheets():
            item = QtWidgets.QListWidgetItem(filename)
            item.filename = filename
            self.list.addItem(item)
        self.list.itemDoubleClicked.connect(self.open_scene)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
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


class SceneModel:
    image = None
    display_image = None
    palette_model = None
    original_palette = None
    filename = None

    def imageqt(self):
        return ImageQt.ImageQt(self.display_image)

    def update_image(self):
        palette1 = self.original_palette
        palette2 = self.palette_model.colors
        self.display_image = switch_colors(self.image, palette1, palette2)


class AnimationModel:
    frame = 0
    data = None
    image = None
    display_image = None
    palette_model = None
    original_palette = None
    filename = None
    layers = []

    def imageqt(self):
        framesize = self.data['frame_size']
        frame = get_frame(self.display_image, framesize, self.frame)
        return ImageQt.ImageQt(frame)

    def update_image(self):
        palette1 = self.original_palette
        palette2 = self.palette_model.colors
        self.display_image = switch_colors(self.image, palette1, palette2)
