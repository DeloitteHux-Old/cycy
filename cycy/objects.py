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

@attributes([Attribute(name="ordinal")], apply_with_init=False)
class W_Char(W_Object):
    def __init__(self, ordinal):
        assert isinstance(ordinal, int)
        assert -(2 ** 7) < 0 < (2 ** 7)
        self.ordinal = ordinal

    def str(self):
        return chr(self.ordinal)


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

    def add(self, other):
        return self.value + other.value

    def sub(self, other):
        return self.value - other.value

@attributes([Attribute(name="value")], apply_with_init=False)
class W_Bool(W_Object):
    def __init__(self, value):
        self.value = bool(value)
