import krita
import math
from PyQt5 import QtGui, QtCore


SRGB_PROFILE = "sRGB-elle-V2-srgbtrc.icc"


def get_node_frames_duration(node, range_in=0, range_out=10):
    durations = [0]
    for i in range(range_in, range_out):
        if node.hasKeyframeAtTime(i):
            durations.append(0)
            continue
        durations[-1] += 1
    return durations


def node_to_qimage(node, width, height):
    """
    Returns an QImage 8-bit sRGB
    """
    size = QtCore.QSize(width, height)
    canvas = QtGui.QImage(size, QtGui.QImage.Format_ARGB32)
    canvas.fill(QtGui.QColor(0, 255, 0))

    is_srgb = (
        node.colorModel() == "RGBA" and
        node.colorDepth() == "U8" and
        node.colorProfile().lower() == SRGB_PROFILE.lower())

    if is_srgb:
        pixel_data = node.projectionPixelData(0, 0, width, height).data()
    else:
        temp_node = node.duplicate()
        temp_node.setColorSpace("RGBA", "U8", SRGB_PROFILE)
        pixel_data = temp_node.projectionPixelData(0, 0, width, height).data()

    image = QtGui.QImage(pixel_data, width, height, QtGui.QImage.Format_ARGB32)
    painter = QtGui.QPainter(canvas)
    painter.drawImage(0, 0, image)

    return canvas


def get_canvas_size(frame_count, column_lenght, frame_width, frame_height):
    row, column = 0, 0
    for _ in range(frame_count):
        column += 1
        if column >= column_lenght:
            column = 0
            row += 1
    return QtCore.QSize(frame_width * column_lenght, frame_height * row)


def fill_canvas(canvas, images, column_lenght, frame_width, frame_height):
    painter = QtGui.QPainter(canvas)
    row, column = 0, 0
    for image in images:
        painter.drawImage(frame_width * column, frame_height * row, image)
        column += 1
        if column >= column_lenght:
            column = 0
            row += 1


def export(filename):
    soft = krita.Krita.instance()
    document = soft.activeDocument()
    width, height = document.bounds().width(), document.bounds().height()
    node = document.activeNode()

    frame_count = sum(
        1 for i in range(document.animationLength())
        if node.hasKeyframeAtTime(i))

    images = []
    for i in range(document.animationLength()):
        if node.hasKeyframeAtTime(i):
            document.setCurrentTime(i)
            images.append(node_to_qimage(node, width, height))
    column_lenght = math.ceil(math.sqrt(frame_count))
    canvas_size = get_canvas_size(frame_count, column_lenght, width, height)
    canvas = QtGui.QImage(canvas_size, QtGui.QImage.Format_ARGB32)
    fill_canvas(canvas, images, column_lenght, width, height)
    canvas.save(filename, "PNG")
    print(get_node_frames_duration(node, range_out=document.animationLength()))


export(r"D:\Works\code\GitHub\pygame_game\data\animations/whitecrowparrot_exploration.png")