"""
This module is a workaround to implement a pointer system for corax.
To be able to save the game state at any moment of the game, using lambda
function is not allowed (unfortunately), this classes definitions a pickelable
and allow the Theatre object to be pickled at any time.
"""

from corax.hitmap import flat_hitmap


class property_collector:
    """
    Meta function to get property of a python object at each moment.
    This is a way to create a pointer to a property and be able to get the
    result at each moment. Properties can be nested.
    Usage:
        class Object():
            @property
            def sub_object(self):
                return Object2()

        class Object2():
            @property
            def text(self):
                return "hello world"

        collector = property_collect(Object(), ['sub_object', 'text'])
        collector()
        >> "hello world"
    """

    def __init__(self, obj, property_names):

        self.obj = obj
        self.property_names = property_names

    def __call__(self):
        value = self.obj
        for property_name in self.property_names:
            value = value.__getattribute__(property_name)
        return value


class item_collector:
    """
    Meta function to get a python object item.
    This is a way to create a pointer to an item and be able to get the
    result at each moment.
    Usage:
        dictionary = {"key": 10}
        collector = item_collector(dictionary, "key")
        collector()
        >> 10
        dictionary["key"] = 25
        collector()
        >> 25
    """

    def __init__(self, obj, item_name):
        self.obj = obj
        self.property_name = item_name

    def __call__(self):
        return self.obj.__getitem__(self.property_name)


class value_collector:
    """
    Serializable version of: "lambda: value"
    Usage:
        collector = value_collector(True)
        collector()
        >> True
    """

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class hitmap_collector:

    def __init__(self, animated, hitmap_name, coordinate=None):
        self.hitmap_name = hitmap_name
        self.coordinate = coordinate
        self.animated = animated

    def __call__(self):
        name = self.hitmap_name
        if self.coordinate:
            return flat_hitmap(
                self.animated.animation_controller.animation.hitmaps.get(name),
                self.animated.coordinate.block_position)
        return self.animated.animation_controller.animation.hitmaps.get(name)
