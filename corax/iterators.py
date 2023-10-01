"""
This is utilities iterators. Unfortunately, for the save system, the yield
keyworkd is forbiden. Each 'generator' has to be written as custom iterable
class.
"""
import uuid
import random
import traceback

from corax.mathutils import linear_ratio


class iter_on_script:
    """
    This iterator recieve a list of functions. All the functions must return
    int representing the number of iteration it needs to be done.
    """
    def __init__(self, script, theatre):
        self.script = script
        self._threatre = theatre
        self._job_index = 0
        self._frame_count = 0

    def __next__(self):

        while self._frame_count == 0:
            if self._job_index >= len(self.script.actions):
                raise StopIteration()
            try:
                job = self.script.create_job(self._job_index, self._threatre)
                self._frame_count = job()
                self._job_index += 1
            except Exception as e:
                print(traceback.format_exc())
                if self.script.actions:
                    error = f'{self.script.actions[self._job_index]}: failed'
                else:
                    error = ""
                print(e)
                raise RuntimeError(f'{error}: {str(job)}') from e

        self._frame_count -= 1


class timer:
    def __init__(self, name, event, length):
        self.name = name
        self.event = event
        self.duration = length
        self.countdown = length
        self.running = False

    def __next__(self):
        if not self.running:
            return
        if self.countdown == 0:
            raise StopIteration()
        self.countdown -= 1

    def stop(self):
        self.countdown = self.duration
        self.running = False

    def start(self):
        self.running = True


class fade:

    def __init__(self, duration, maximum, reverse=False):
        self.duration = duration
        self.maximum = maximum
        self.reverse = reverse
        self._index = 0

    def __next__(self):
        if self._index > self.duration:
            raise StopIteration()
        result = self.maximum * linear_ratio(self._index, 0, self.duration)
        self._index += 1
        return self.maximum - result if self.reverse else result


class frame_data_iterator:

    def __init__(self, frame_data):
        self.frame_data = frame_data
        self._findex = 0
        self._durations = self.frame_data[self._findex].get('duration', 1)
        self._index = 0

    def __next__(self):
        if self._index >= len(self._durations):
            self._index = 0
            self._findex += 1
            data = self.frame_data.get(self._findex)
            if data is None:
                raise StopIteration()
            self._durations = data.get('duration', 1)
        return self._durations[self._index]


class shuffle:

    def __init__(self, array, no_repeat=True):
        self.array = array
        self.no_repeat = no_repeat
        self._last = None

    def __next__(self):
        while True:
            element = random.choice(self.array)
            if self.no_repeat is True and element == self._last:
                continue
            self._last = element
            return element


class cycle:
    # This class has to be reimplemented from itertools.cycle to be picklable.
    def __init__(self, array):
        self.original_array = array[:]
        self.current_array = []

    @property
    def value(self):
        if not self.current_array:
            return self.original_array[0]
        return self.current_array[0]

    def __next__(self):
        while True:
            if not self.current_array:
                self.current_array = self.original_array[:]
            return self.current_array.pop(0)


def choose(items):
    """
    this method is an utils to choose an element with a coefficient.
    :items: is a dict {'item1': coefficient as int}
    return a random key with a chance coefficient as value
    """
    return random.choice([
        t for k, v in items.items()
        for t in tuple([k] * v) if v])
