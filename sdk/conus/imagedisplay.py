from PySide6 import QtWidgets, QtGui, QtCore
from conus.qtutils import shift_pressed, alt_pressed
from conus.slider import Slider


class AnimationDisplay(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.animations = QtWidgets.QListWidget()
        self.animations.addItems(model.data['evaluation_order'])
        self.animations.itemDoubleClicked.connect(self.animation_changed)
        self.animations.setFocusPolicy(QtCore.Qt.NoFocus)

        self.animation = QtWidgets.QWidget()
        self.imagedisplay = ImageDisplay(model)
        self.slider = Slider()
        self.slider.valueChanged.connect(self.change_frame)

        self.vlayout = QtWidgets.QVBoxLayout(self.animation)
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.addWidget(self.imagedisplay)
        self.vlayout.addWidget(self.slider)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.animation)
        self.splitter.addWidget(self.animations)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.splitter)
        self.set_animation(model.data['evaluation_order'][0])

    def set_animation(self, name):
        mdata = self.model.data['moves'][name]
        self.slider.minimum = mdata['start_at_image']
        maxmium = self.slider.minimum + len(mdata['frames_per_image'])
        self.slider.maximum = maxmium
        self.slider.value = self.slider.minimum
        self.model.frame = self.slider.minimum
        self.imagedisplay.repaint()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.reset()

    def reset(self):
        self.imagedisplay.viewportmapper.viewsize = self.imagedisplay.rect()
        img = self.model.imageqt()
        size = img.size()
        rect = QtCore.QRectF(0, 0, size.width(), size.height())
        self.imagedisplay.viewportmapper.focus(rect)
        self.repaint()

    def animation_changed(self, item):
        self.set_animation(item.text())

    def change_frame(self, frame):
        self.model.frame = frame
        self.imagedisplay.repaint()


class ImageDisplay(QtWidgets.QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.viewportmapper = ViewportMapper()
        self.viewportmapper.viewsize = QtCore.QSize(*model.display_image.size)
        self.modemanager = ModeManager()
        self.reset()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.reset()

    def showEvent(self, _):
        self.reset()

    def reset(self):
        self.viewportmapper.viewsize = self.rect().size()
        img = self.model.display_image
        size = img.size
        rect = QtCore.QRectF(0, 0, size[0], size[1])
        self.viewportmapper.focus(rect)
        self.repaint()

    def sizeHint(self):
        return QtCore.QSize(*self.model.display_image.size)

    def paintEvent(self, _):
        if not self.model:
            return
        painter = QtGui.QPainter(self)
        painter.setBrush(QtCore.Qt.black)
        painter.setPen(QtCore.Qt.transparent)
        painter.drawRect(self.rect())
        painter.setBrush(QtCore.Qt.darkBlue)
        img = self.model.imageqt()
        size = img.size()
        rect = QtCore.QRectF(0, 0, size.width(), size.height())
        rect = self.viewportmapper.to_viewport_rect(rect)
        painter.drawRect(rect)
        painter.drawImage(rect, img)
        painter.end()

    def resizeEvent(self, event):
        self.viewportmapper.viewsize = self.size()
        size = (event.size() - event.oldSize()) / 2
        offset = QtCore.QPointF(size.width(), size.height())
        self.viewportmapper.origin -= offset
        self.repaint()

    def mousePressEvent(self, event):
        self.modemanager.update(event, pressed=True)

    def mouseReleaseEvent(self, event):
        self.modemanager.update(event, pressed=False)

    def wheelEvent(self, event):
        # To center the zoom on the mouse, we save a reference mouse position
        # and compare the offset after zoom computation.
        factor = .25 if event.angleDelta().y() > 0 else -.25
        self.zoom(factor, event.position())
        self.repaint()

    def zoom(self, factor, reference):
        abspoint = self.viewportmapper.to_units_coords(reference)
        if factor > 0:
            self.viewportmapper.zoomin(abs(factor))
        else:
            self.viewportmapper.zoomout(abs(factor))
        relcursor = self.viewportmapper.to_viewport_coords(abspoint)
        vector = relcursor - reference
        self.viewportmapper.origin = self.viewportmapper.origin + vector

    def mouseMoveEvent(self, event):
        if self.modemanager.mode == ModeManager.ZOOMING:
            offset = self.modemanager.mouse_offset(event.pos())
            if offset is not None and self.modemanager.zoom_anchor:
                factor = (offset.x() + offset.y()) / 10
                self.zoom(factor, self.modemanager.zoom_anchor)

        elif self.modemanager.mode == ModeManager.NAVIGATION:
            offset = self.modemanager.mouse_offset(event.pos())
            if offset is not None:
                self.viewportmapper.origin = (
                    self.viewportmapper.origin - offset)
        self.repaint()


class ViewportMapper():
    """
    Used to translate/map between:
        - abstract/data/units coordinates
        - viewport/display/pixels coordinates
    """
    def __init__(self):
        self.zoom = 1
        self.origin = QtCore.QPointF(0, 0)
        # We need the viewport size to be able to center the view or to
        # automatically set zoom from selection:
        self.viewsize = QtCore.QSize(300, 300)

    def to_viewport(self, value):
        return value * self.zoom

    def to_units(self, pixels):
        return pixels / self.zoom

    def to_viewport_coords(self, units_point):
        return QtCore.QPointF(
            self.to_viewport(units_point.x()) - self.origin.x(),
            self.to_viewport(units_point.y()) - self.origin.y())

    def to_units_coords(self, pixels_point):
        return QtCore.QPointF(
            self.to_units(pixels_point.x() + self.origin.x()),
            self.to_units(pixels_point.y() + self.origin.y()))

    def to_viewport_rect(self, units_rect):
        return QtCore.QRectF(
            (units_rect.left() * self.zoom) - self.origin.x(),
            (units_rect.top() * self.zoom) - self.origin.y(),
            units_rect.width() * self.zoom,
            units_rect.height() * self.zoom)

    def to_units_rect(self, pixels_rect):
        top_left = self.to_units_coords(pixels_rect.topLeft())
        width = self.to_units(pixels_rect.width())
        height = self.to_units(pixels_rect.height())
        return QtCore.QRectF(top_left.x(), top_left.y(), width, height)

    def zoomin(self, factor=10.0):
        self.zoom += self.zoom * factor
        self.zoom = min(self.zoom, 5.0)

    def zoomout(self, factor=10.0):
        self.zoom -= self.zoom * factor
        self.zoom = max(self.zoom, .1)

    def center_on_point(self, units_center):
        """Given current zoom and viewport size, set the origin point."""
        self.origin = QtCore.QPointF(
            units_center.x() * self.zoom - self.viewsize.width() / 2,
            units_center.y() * self.zoom - self.viewsize.height() / 2)

    def focus(self, units_rect):
        self.zoom = min([
            float(self.viewsize.width()) / units_rect.width(),
            float(self.viewsize.height()) / units_rect.height()])
        if self.zoom > 1:
            self.zoom *= 0.7  # lower zoom to add some breathing space
        self.zoom = max(self.zoom, .1)
        self.center_on_point(units_rect.center())


class ModeManager:
    FLY_OVER = 'fly_over'
    NAVIGATION = 'navigation'
    ZOOMING = 'zooming'

    def __init__(self):
        self.shapes = []
        self.left_click_pressed = False
        self.right_click_pressed = False
        self.middle_click_pressed = False
        self.mouse_ghost = None
        self.anchor = None
        self.zoom_anchor = None

    def update(
            self,
            event,
            pressed=False,
            has_shape_hovered=False,
            dragging=False):

        self.dragging = dragging
        self.has_shape_hovered = has_shape_hovered
        self.update_mouse(event, pressed)

    def update_mouse(self, event, pressed):
        if event.button() == QtCore.Qt.LeftButton:
            self.left_click_pressed = pressed
            self.anchor = event.pos() if self.dragging else None
        elif event.button() == QtCore.Qt.RightButton:
            self.right_click_pressed = pressed
        elif event.button() == QtCore.Qt.MiddleButton:
            self.middle_click_pressed = pressed

    @property
    def mode(self):
        if shift_pressed() and alt_pressed():
            return ModeManager.ZOOMING
        elif self.middle_click_pressed:
            return ModeManager.NAVIGATION
        self.mouse_ghost = None
        return ModeManager.FLY_OVER

    def mouse_offset(self, position):
        result = position - self.mouse_ghost if self.mouse_ghost else None
        self.mouse_ghost = position
        return result or None
