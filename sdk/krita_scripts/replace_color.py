import krita
from PyQt5 import QtCore


COLORS_TO_ERASE = [
    [170, 161, 150],
    [62, 54, 43]
]


soft = krita.Krita.instance()
document = soft.activeDocument()
node = document.activeNode()
h, w = document.height(), document.width()


pixel_data = node.pixelData(0, 0, w, h)
new_pixel_data = QtCore.QByteArray()
pixel_found = 0
for i in range(0, pixel_data.length(), 4):
    bgr = [ord(d) for d in pixel_data[i:i+3]]
    color = pixel_data[i:i+4] if bgr not in COLORS_TO_ERASE else b'\x00\xff\x00\xff'
    if bgr in COLORS_TO_ERASE :
        pixel_found += 1
    new_pixel_data.append(color)
node.setPixelData(new_pixel_data, 0, 0, w, h)
document.refreshProjection()