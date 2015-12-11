"""
C-runtime level wrapper objects (boxes).

"""

from characteristic import Attribute, attributes


class W_Object(object):
    """
    Base class for C objects.

    """

    def rint(self):
        raise NotImplementedError()


@attributes([])
class _W_Null(W_Object):
    pass


W_NULL = _W_Null()


@attributes([Attribute(name="char")], apply_with_init=False)
class W_Char(W_Object):
    def __init__(self, char):
        assert isinstance(char, str)
        assert len(char) == 1
        self.char = char

    def neq(self, other):
        return ord(self.char[0]) != other.rint()

    def dump(self):
        return "(char)'%s'" % self.char


@attributes([Attribute(name="value")], apply_with_init=False)
class W_String(W_Object):
    def __init__(self, value):
        assert isinstance(value, str)
        self.value = value

    def dereference(self, index):
        assert isinstance(index, W_Int32)
        rint = index.rint()
        if len(self.value) == rint:
            return "\0"
        return self.value[rint]

    def dump(self):
        return '(char *)"%s"' % self.value


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

    def dump(self):
        return "(int32_t)%s" % self.value

    def rint(self):
        return self.value


@attributes([Attribute(name="value")], apply_with_init=False)
class W_Bool(W_Object):
    def __init__(self, value):
        self.value = bool(value)

    def is_true(self):
        return self.value == True

    def dump(self):
        return "(bool)%s" % str(self.value).lower()


@attributes(
    [
        Attribute(name="name"),
        Attribute(name="arity"),
        Attribute(name="bytecode"),
    ],
    apply_with_init=False,
)
class W_Function(W_Object):
    def __init__(self, name, arity, bytecode):
        self.name = name
        self.arity = arity
        self.bytecode = bytecode

    def call(self, interpreter, arguments):
        return interpreter.run(self.bytecode, arguments=arguments)

    def dump(self):
        return "(function)%s" % self.name
