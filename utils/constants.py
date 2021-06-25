import enum

messages = {
    "ms": {"en": " m/s", "ru": " м/с"},
    "feels_like": {"en": "feels like: ", "ru": "ощущается как: "},
}


def make_enum(name, values) -> enum.Enum:
    _k = _v = None

    class TheEnum(enum.Enum):
        nonlocal _k, _v
        for _k, _v in values.items():
            locals()[_k] = _k

    TheEnum.__name__ = name
    return TheEnum
    # https://stackoverflow.com/questions/47299036/how-can-i-construct-an-enum-enum-from-a-dictionary-of-values


LANGUAGES = make_enum("LANGUAGES", messages["ms"])
