from PyQt5 import QtGui, QtCore, QtWidgets


WORD_TYPES = [
    {
        'exp': r'\b' + r'\b|\b'.join(["script"]) + r'\b',
        'color': 'red',
        'bold': True,
        'italic': False
    },
    {
        'exp': r'\b' + r'\b|\b'.join(["is", "in", "by"]) + r'\b',
        'color': '#0088FF',
        'bold': True,
        'italic': False
    },
    {
        'exp': r'\b' + r'\b|\b'.join(["run", "play", "pressed", "set", "reach"]) + r'\b',
        'color': '#FF5522',
        'bold': True,
        'italic': False
    },
    {
        'exp': r'\b' + r'\b|\b'.join(["scene", "animation", "hitbox", "key", "player", "zone", "movesheet"]) + r'\b',
        'color': '#00AA33',
        'bold': True,
        'italic': False
    },
    {
        'exp':r'//[^\n]*',
        'color': '#226600',
        'bold': False,
        'italic': True
    }
]


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


class CrackleHighlighter(QtGui.QSyntaxHighlighter):

    def __init__(self, document=None):
        super(CrackleHighlighter, self).__init__(document)
        self.rules = []
        for data in WORD_TYPES:
            text_format = create_textcharformat(
                color=data['color'],
                bold=data['bold'],
                italic=data['italic'])
            rule = QtCore.QRegExp(data['exp']), text_format
            print (data['exp'])
            self.rules.append(rule)

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format_)
                index = expression.indexIn(text, index + length)


app = QtWidgets.QApplication([])
plaintext_editor = QtWidgets.QPlainTextEdit()

test = """

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

h = CrackleHighlighter(plaintext_editor.document())
plaintext_editor.setPlainText(test)
plaintext_editor.show()
app.exec_()