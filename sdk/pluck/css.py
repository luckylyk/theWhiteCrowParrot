import os


def get_css(filename):
    path = os.path.join(os.path.dirname(__file__), "css", filename)
    with open(path, "r") as f:
        return f.read()