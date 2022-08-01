import krita


class Kritax(krita.Extension):

    def setup(self):
        return

    def createActions(self, window):
        action = window.createAction(
            "open_kritax",
            "Kritax",
            "tools")
        action.triggered.connect(lambda: True)
