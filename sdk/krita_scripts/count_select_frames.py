import krita
import math
from PyQt5 import QtGui, QtCore


def get_node_frames_duration(node, range_in=0, range_out=10):
    durations = []
    for i in range(range_in, range_out):
        if node.hasKeyframeAtTime(i):
            durations.append(1)
            continue
        durations[-1] += 1
    return [f * 2 for f in durations]


soft = krita.Krita.instance()
document = soft.activeDocument()
node = document.activeNode()
start = document.playBackStartTime()
end = document.playBackEndTime()


print(get_node_frames_duration(node, range_in=start, range_out=end))