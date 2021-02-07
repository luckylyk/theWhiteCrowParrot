from PyQt5 import QtGui, QtCore, QtWidgets


RULES = {
    'crackle':
        [
            {
                'exp': r'\b' + r'\b|\b'.join(["script"]) + r'\b',
                'color': '#FF8855',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'\b' + r'\b|\b'.join(["is", "in", "by"]) + r'\b',
                'color': '#88CCFF',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'\b' + r'\b|\b'.join(["run", "play", "pressed", "set", "reach"]) + r'\b',
                'color': '#FFDD55',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'\b' + r'\b|\b'.join(["scene", "animation", "hitbox", "key", "player", "zone", "movesheet"]) + r'\b',
                'color': '#88FFCC',
                'bold': True,
                'italic': False
            },
            {
                'exp':r'//[^\n]*',
                'color': '#558855',
                'bold': False,
                'italic': True
            },
            {
                'exp': r'[^\n ]*:',
                'color': 'grey',
                'bold': False,
                'italic': True
            }
        ],
    'json':
        [
            {
                'exp': r'[,-\[\]\{\}]+',
                'color': 'white',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'[0-9]+',
                'color': '#88FFCC',
                'bold': False,
                'italic': False
            },
            {
                'exp': r'"[^\n]*"',
                'color': '#FFCC88',
                'bold': False,
                'italic': True
            },
            {
                'exp': r'"[^\n]*":',
                'color': '#66CCFF',
                'bold': True,
                'italic': False
            }
        ]
}


def create_textcharformat(color, bold=False, italic=False):
    char_format = QtGui.QTextCharFormat()
    qcolor = QtGui.QColor()
    if isinstance(color, str):
        qcolor.setNamedColor(color)
    else:
        r, g, b = color
        qcolor.setRgbF(r, g, b)
    char_format.setForeground(qcolor)
    if bold:
        char_format.setFontWeight(QtGui.QFont.Bold)
    if italic:
        char_format.setFontItalic(True)
    return char_format


class CoraxHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, rules, document=None):
        super(CoraxHighlighter, self).__init__(document)
        self.rules = []
        for data in rules:
            text_format = create_textcharformat(
                color=data['color'],
                bold=data['bold'],
                italic=data['italic'])
            rule = QtCore.QRegExp(data['exp']), text_format
            self.rules.append(rule)

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format_)
                index = expression.indexIn(text, index + length)



if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    plaintext_editor = QtWidgets.QPlainTextEdit()

    test = (
"""
script go_to_tente_with_sword
    key UP is pressed
    scene is forest_01
    player whitecrow: movesheet is whitecrowparrot_sword.json
    player whitecrow: animation is idle
    player whitecrow: hitbox foot in zone tente
        player whitecrow: play animation tidy_up_sword
        run go_to_tente

    //fuck that bitch

script go_to_tente_forced //check my dick
    scene is forest_01
    // it's ok
        // still ok
// I love you
    player whitecrow: movesheet is whitecrowparrot_exploration
    player whitecrow: animation is idle
    player whitecrow: hitbox foot in zone tente //try this
        player whitecrow: reach (52, 35) by (walk, footsie)
        player whitecrow: play through_door
"""

"""test = {
    "type": "set_static",
    "file": "forest_01/fg_grass_02.png",
    "position": [769, 154],
    "deph": 0.23
}
{
    "type": "set_static",
    "file": "forest_01/l_montain.png",
    "position": [509, 116],
    "deph": -0.42
}
{
    "type": "set_static",
    "file": "forest_01/mid_bg_bush.png",
    "position": [3391, 185],
    "deph": -0.2
}
{
    "type": "set_static",
    "file": "forest_01/grass_01.png",
    "position": [881, 222],
    "deph": -0.05
}
""")


    h = CoraxHighlighter(RULES["json"], document=plaintext_editor.document())
    qfont = QtGui.QFont("Consolas")
    qfont.setPixelSize(15)
    plaintext_editor.setFont(qfont)
    plaintext_editor.setPlainText(test)
    plaintext_editor.show()
    plaintext_editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
    import os
    stylesheetpath = os.path.join(os.path.dirname(__file__), "flatdark.css")
    stylesheet = ""
    with open(stylesheetpath, "r") as f:
        for line in f:
            stylesheet += line


    app.setStyleSheet(stylesheet)
    app.exec_()
