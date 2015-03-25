from characteristic import Attribute, attributes
from rpython.tool.pairtype import extendabletype

from rply.token import BaseBox


class Node(BaseBox):
    # Allows using __extend__ to extend the type
    __metaclass__ = extendabletype


@attributes(
    [
        Attribute(name="operator"),
        Attribute(name="left"),
        Attribute(name="right"),
    ],
    apply_with_init=False,
)
class BinaryOperation(Node):
    def __init__(self, operator, left, right):
        assert operator in ("+", "-", "!=") # for now
        self.operator = operator
        self.left = left
        self.right = right


@attributes(
    [
        Attribute(name="name"),
        Attribute(name="vtype"),
        Attribute(name="value"),
    ],
    apply_with_init=False,
)
class VariableDeclaration(Node):
    def __init__(self, name, vtype, value):
        assert vtype == "INT32"
        self.name = name
        self.vtype = vtype
        self.value = value


@attributes([Attribute(name="value")], apply_with_init=False)
class Int32(Node):
    def __init__(self, value):
        assert isinstance(value, int)
        assert -2**32 < value <= 2**32-1
        self.value = value


@attributes([Attribute(name="name")], apply_with_init=False)
class Variable(Node):
    def __init__(self, name):
        self.name = name


@attributes(
    [
        Attribute(name="operator"),
        Attribute(name="variable"),
    ],
    apply_with_init=False,
)
class PostOperation(Node):
    def __init__(self, operator, variable):
        assert operator in ("++", "--")
        self.operator = operator
        self.variable = variable


@attributes(
    [Attribute(name="left"), Attribute(name="right")],
    apply_with_init=False,
)
class Assignment(Node):
    def __init__(self, left, right):
        assert isinstance(left, Variable)
        self.left = left
        self.right = right


@attributes([Attribute(name="value")], apply_with_init=False)
class Array(Node):
    def __init__(self, value):
        _type = type(value[0])
        for v in value:
            assert isinstance(v, _type)
        self.value = value


@attributes([Attribute(name="value")], apply_with_init=False)
class Char(Node):
    def __init__(self, value):
        # TODO handle escaped chars
        assert isinstance(value, str) and len(value) == 1
        self.value = value


@attributes(
    [
        Attribute(name="array"),
        Attribute(name="index"),
    ],
    apply_with_init=False,
)
class ArrayDereference(Node):
    def __init__(self, array, index):
        self.array = array
        self.index = index

@attributes(
    [Attribute(name="value")],
    apply_with_init=False
)
class ReturnStatement(Node):
    def __init__(self, value):
        self.value = value
