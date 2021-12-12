
from copy import copy


def match_arrays_length(array, reference, default=None):
    if len(array) == len(reference):
        return array
    elif len(array) < len(reference):
        return array[:len(reference)]

    return array + [copy(default) for _ in range(len(array) - len(reference))]
