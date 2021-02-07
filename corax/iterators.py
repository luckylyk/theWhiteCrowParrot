
import random


def itertable(a, b):
    for i in range(a):
        for j in range(b):
            yield i, j


def frame_data_iterator(frame_data):
    for i, data in enumerate(frame_data):
        duration = data.get("duration", 1)
        for _ in range(duration):
            yield i


def shuffle(array, no_repeat=True):
    last = None
    while True:
        element = random.choice(array)
        if no_repeat is True and element == last:
            continue
        last = element
        yield element