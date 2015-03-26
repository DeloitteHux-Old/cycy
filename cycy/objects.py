"""
C-runtime level wrapper objects (boxes).

"""

from characteristic import Attribute, attributes


class W_Object(object):
    """
    Base class for C objects.

    """


@attributes([])
class _W_Null(W_Object):
    pass

w_null = _W_Null()

@attributes([Attribute(name="char")], apply_with_init=False)
class W_Char(W_Object):
    def __init__(self, char):
        assert isinstance(char, str)
        assert len(char) == 1
        self.char = char


@attributes([Attribute(name="value")], apply_with_init=False)
class W_Int32(W_Object):
    def __init__(self, value):
        assert isinstance(value, int)
        assert -2**32 <= value < 2**32
        self.value = value

    def leq(self, other):
        return self.value <= other.value

    def neq(self, other):
        return self.value != other.value


@attributes([Attribute(name="value")], apply_with_init=False)
class W_Bool(W_Object):
    def __init__(self, value):
        self.value = bool(value)


@attributes([Attribute(name="name"), Attribute(name="num_args")], apply_with_init=False)
class W_Function(W_Object):
    def __init__(self, name, num_args):
        self.name = name
        self.num_args = num_args
