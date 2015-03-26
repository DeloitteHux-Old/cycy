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

    def neq(self, other):
        if isinstance(other, W_Int32):
            return ord(self.char[0]) != other.value
        raise NotImplementedError()

@attributes([Attribute(name="value")], apply_with_init=False)
class W_String(W_Object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.value = value

    def dereference(self, index):
        assert isinstance(index, W_Int32)
        if len(self.value) == index.value:
            return "\0"
        return self.value[index.value]


@attributes([Attribute(name="value")], apply_with_init=False)
class W_Int32(W_Object):
    def __init__(self, value):
        assert isinstance(value, int)
        assert -2**32 <= value < 2**32
        self.value = value

    def is_true(self):
        return self.value != 0

    def leq(self, other):
        return self.value <= other.value

    def neq(self, other):
        return self.value != other.value

    def add(self, other):
        return self.value + other.value

    def sub(self, other):
        return self.value - other.value

    def str(self):
        return str(self.value)


@attributes([Attribute(name="value")], apply_with_init=False)
class W_Bool(W_Object):
    def __init__(self, value):
        self.value = bool(value)

    def is_true(self):
        return self.value == True


@attributes([Attribute(name="name"), Attribute(name="num_args")], apply_with_init=False)
class W_Function(W_Object):
    def __init__(self, name, num_args):
        self.name = name
        self.num_args = num_args
