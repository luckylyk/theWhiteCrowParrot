
import math


def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    return value


def difference(n1, n2):
    n1, n2 = sorted([n1, n2])
    if n1 < 0 > n2:
        return abs(n1 - n2)
    elif n1 > 0 < n2:
        return abs(n2 - n1)
    return abs(abs(n1) + n2)


def normalize(value, minimum=0, maximum=1):
    assert minimum <= maximum
    offset = difference(minimum, maximum)
    if offset == 0:
        return minimum if minimum < value else maximum
    while not minimum <= value <= maximum:
        value += offset if value < minimum else -offset
    return value


def linear_ratio(value, minimum=0, maximum=100):
    assert minimum <= maximum
    return (1 - ((value - minimum) / (maximum - minimum)))
