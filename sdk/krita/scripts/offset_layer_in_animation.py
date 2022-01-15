import krita
import time

soft = krita.Krita.instance()
document = soft.activeDocument()
width, height = document.bounds().width(), document.bounds().height()
node = document.activeNode()
offset = (-40, 20)
range_in, range_out = 195, 235

for i in range(range_in, range_out):
    if not node.hasKeyframeAtTime(i):
        continue
    document.setCurrentTime(i)
    print(node.position())
    continue
    node.move(*offset)
    time.sleep(0.1)
