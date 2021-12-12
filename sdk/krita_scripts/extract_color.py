import krita
from PySide6 import QtCore


COLORS_TO_EXTRACT = [
    [156, 164, 157],
    [116, 111, 86]]


soft = krita.Krita.instance()
document = soft.activeDocument()
node = document.nodeByName("Background")
extract_node = document.activeNode()
start = document.playBackStartTime()
end = document.playBackEndTime()
h, w = document.height(), document.width()
document.modified()

if node.hasKeyframeAtTime(document.currentTime()):
    extracted_data = QtCore.QByteArray()
    document.refreshProjection()
    pixel_data = node.pixelData(0, 0, w, h)
    soft.action('add_blank_frame').trigger()
    for i in range(0, pixel_data.length(), 4):
        bgr = [ord(d) for d in pixel_data[i:i+3]]
        color = pixel_data[i:i+4] if bgr in COLORS_TO_EXTRACT else '\x00\x00\x00\x00'
        extracted_data.append(color)
    extract_node.setPixelData(extracted_data, 0, 0, w, h)

    soft.action('insert_keyframe_right').trigger()
























import krita
from PySide6 import QtCore
import time


COLORS_TO_EXTRACT = [
    [156, 164, 157],
    [116, 111, 86]]


soft = krita.Krita.instance()
document = soft.activeDocument()
root = document.rootNode()
node = document.activeNode()
new_node = document.createNode("extracted", "paintlayer")
new_node.enableAnimation()
root.addChildNode(new_node, None)
document.setActiveNode(new_node)
start = document.playBackStartTime()
end = document.playBackEndTime()
h, w = document.height(), document.width()
document.modified()
soft.action("pin_to_timeline")
