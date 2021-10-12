from PyQt5 import QtGui, QtWidgets, QtCore
import sys
import PIL.Image
import math
import os

def fill_canvas(canvas, images, column_lenght, frame_width, frame_height):
    painter = QtGui.QPainter(canvas)
    row, column = 0, 0
    for image in images:
        painter.drawImage(frame_width * column, frame_height * row, image)
        column += 1
        if column >= column_lenght:
            column = 0
            row += 1

def get_canvas_size(frame_count, column_lenght, frame_width, frame_height):
    row, column = 1, 0
    for _ in range(frame_count):
        column += 1
        if column >= column_lenght:
            column = 0
            row += 1
    return QtCore.QSize(frame_width * column_lenght, frame_height * row)

# app = QtWidgets.QApplication(sys.argv)
PATH = r"C:\Users\lio\Desktop\fight\export_2_body"
OUTPUT = r"D:\Works\code\GitHub\theWhiteCrowParrot\whitecrowparrot\animations\test_2.png"
images = [os.path.join(PATH, f) for f in os.listdir(PATH)]
width, height = PIL.Image.open(images[0]).size
images = [QtGui.QImage(image) for image in images]
column_lenght = math.ceil(math.sqrt(len(images)))

canvas_size = get_canvas_size(len(images), column_lenght, width, height)
canvas = QtGui.QImage(canvas_size, QtGui.QImage.Format_ARGB32)
fill_canvas(canvas, images, column_lenght, width, height)
canvas.save(OUTPUT, "PNG")
