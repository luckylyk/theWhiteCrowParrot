BOOL_AS_STRING = ['false', 'true']


def object_type(obj):
    if not obj.count("."):
        msg = f"{obj}: Object must start with an object type"
        raise SyntaxError(msg)
    return obj.split(".")[0].strip(' ')


def object_name(obj):
    if not obj.count("."):
        msg = "Object must have an oject name in second position"
        raise SyntaxError(msg)
    return obj.split(".")[1].strip(' ')


def object_attribute(obj):
    if obj.count(".") < 2:
        raise ValueError(f"No attibute specified for \"{obj}\"")
    return ".".join(obj.split(".")[2:]).strip(' ')


def string_to_int_list(string):
    try:
        return [int(n) for n in string.strip("()").split(",")]
    except ValueError:
        raise ValueError(f'{string} is not convertible to int list.')


def string_to_string_list(string):
    return [s.strip(" ") for s in string.strip("()").split(",")]


def string_to_bool(string):
    return string == "true"
