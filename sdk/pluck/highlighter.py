from PySide6 import QtGui, QtCore, QtWidgets

ACTION_KEYWORDS = ["run", "play", "set", "reach", "move"]


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
                'exp': r'\b' + r'\b|\b'.join(["always", "is", "in", "cross", "has", "by"]) + r'\b',
                'color': '#88CCFF',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'\b' + r'\b|\b'.join(ACTION_KEYWORDS) + r'\b',
                'color': '#FFDD55',
                'bold': True,
                'italic': False
            },
            {
                'exp': r'\b' + r'\b|\b'.join(["theatre", "scene", "gamepad", "name", "pressed", "animation", "hitbox", "key", "player", "zone", "sheet"]) + r'\b',
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
            rule = QtCore.QRegularExpression(data['exp']), text_format
            self.rules.append(rule)

    def highlightBlock(self, text):
        for pattern, format_ in self.rules:
            expression = QtCore.QRegularExpression(pattern)
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(index, length, format_)
            # index = expression.indexIn(text)
            # while index >= 0:
            #     length = expression.matchedLength()
            #     self.setFormat(index, length, format_)
            #     index = expression.indexIn(text, index + length)


def get_plaint_text_editor(rule="crackle"):
    plaintext_editor = QtWidgets.QPlainTextEdit()
    highlighter = CoraxHighlighter(RULES[rule], document=plaintext_editor.document())
    qfont = QtGui.QFont("Consolas")
    qfont.setPixelSize(15)
    plaintext_editor.setFont(qfont)
    plaintext_editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
    return plaintext_editor, highlighter


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    plaintext_editor = QtWidgets.QPlainTextEdit()

    test = """
// this is a test script to describe how i would like to design that language


script go_to_tente_with_sword
    gamepad.keys.pressed has UP
    theatre.scene.name is forest
    player.whitecrow.sheet is whitecrowparrot_sword.json
    player.whitecrow.animation is idle
 //   player.whitecrow.hitbox.foot cross zone.tente
        player.whitecrow play tidy_up_sword
        run go_to_tente

 // commentary test

script go_to_tente // commentary test
    gamepad.keys.pressed has UP
    theatre.scene.name is forest
    player.whitecrow.sheet is whitecrowparrot_exploration.json
    player.whitecrow.animation is idle
 // commentary test
     // commentary test
 //   player.whitecrow.hitbox.foot in zone.tente //try this
//      player.whitecrow reach (52, 35) by (walk, footsie)
        player.whitecrow play through_door
        theatre.scene set tente
        player.whitecrow play walk_a
        player.whitecrow play walk_b
        player.whitecrow play idle


script go_to_forest // commentary test
    true
        theatre.scene set forest"""

    h = CoraxHighlighter(RULES["crackle"], document=plaintext_editor.document())
    qfont = QtGui.QFont("Consolas")
    qfont.setPixelSize(15)
    plaintext_editor.setFont(qfont)
    plaintext_editor.setPlainText(test)
    plaintext_editor.show()
    plaintext_editor.setWordWrapMode(QtGui.QTextOption.NoWrap)
    import os
    stylesheetpath = os.path.join(os.path.dirname(__file__), "css/flatdark.css")
    stylesheet = ""
    with open(stylesheetpath, "r") as f:
        for line in f:
            stylesheet += line


    app.setStyleSheet(stylesheet)
    app.exec()
