
import random
import traceback

from corax.mathutils import linear_ratio


def iter_on_jobs(jobs, actions=None):
    """
    This iterator recieve a list of functions. All the functions must return
    int representing the number of iteration it needs to be done.
    """
    for i, job in enumerate(jobs):
        try:
            frame_count = job()
        except Exception:
            print(traceback.format_exc())
            error = actions[i] + ": failed" if actions else ""
            raise ValueError(error)
        while frame_count > 0:
            yield
            frame_count -= 1


def fade(duration, maximum=255, reverse=False):
    """
    This iterator yield a progressive value between 0 and a maximum value.
    """
    for i in range(duration + 1):
        result = maximum * linear_ratio(i, 0, duration)
        yield maximum - result if reverse else result


def itertable(a, b):
    """
    Bi-dimensional iterator.
    """
    for i in range(a):
        for j in range(b):
            yield i, j


def frame_data_iterator(frame_data):
    for i, data in enumerate(frame_data):
        duration = data.get("duration", 1)
        for _ in range(duration):
            yield i


def shuffle(array, no_repeat=True):
    """
    Iterate randomly on an array.
    """
    last = None
    while True:
        element = random.choice(array)
        if no_repeat is True and element == last:
            continue
        last = element
        yield element


def choose(items):
    '''
    this method is an utils to choose an element with a coefficient.
    :items: is a dict {'item1': coefficient as int}
    return a random key with a chance coefficient as value
    '''
    return random.choice([
        t for k, v in items.items()
        for t in tuple([k] * v) if v])