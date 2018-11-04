"""
A simple module
"""

_GREETINGS = {
    'en': "Hello",
    'se': "Hej",
}


def greet(lang: str) -> str:
    """
    A simple function
    """

    try:
        return _GREETINGS[lang]
    except KeyError:
        raise ValueError(
            "Expected lang to be one of {} but found {}".format(
                ', '.join(_GREETINGS), lang
            )
        )
