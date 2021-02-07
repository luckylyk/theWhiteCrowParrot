
import math


def clamp(value, minimum, maximum):
    """
    Clamp a value done in the range: minimum, maximum.
    """
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    return value


def difference(n1, n2):
    """
    Return the difference between two numbers.
    """
    n1, n2 = sorted([n1, n2])
    if n1 < 0 > n2:
        return abs(n1 - n2)
    elif n1 > 0 < n2:
        return abs(n2 - n1)
    return abs(abs(n1) + n2)


def normalize(value, minimum=0, maximum=1):
    """
    Offset the value to put it in between the minimum and the maximum given.
    Note that it is different of the Clamp which return the max or the min if
    the value is out of range. Here the value is offset by the range until it
    does fit in.
    """
    assert minimum <= maximum
    offset = difference(minimum, maximum)
    if offset == 0:
        return minimum if minimum < value else maximum
    while not minimum <= value <= maximum:
        value += offset if value < minimum else -offset
    return value


def linear_ratio(value, minimum=0, maximum=100):
    """
    Return a linear position a float of the value between minimum and maximum.
    Examples:
        value=5, minum=0, maximum=10, result=0.5
        value=5, minum=0, maximum=5, result=1
        value=12, minum=10, maximum=20, result=0.2
    """
    assert minimum <= maximum
    return (1 - ((value - minimum) / (maximum - minimum)))


def sum_num_arrays(*narrays):
    """
    Add n arrays together. All given arrays MUST be the same length.
    Example:
        input: (0, 3, 6), (5, 1, 0), (2, 2, 2), (1, 0, 0), (3, 1, 2)
        output: (0 + 5 + 2 + 1 + 3, 3 + 1 + 2 + 0 + 1, 6 + 0 + 2 + 0 + 2)
                (11, 7, 10)
    """
    return [
        sum(narray[i] for narray in narrays)
        for i in range(len(narrays[0]))]