from characteristic import Attribute, attributes
from rpython.tool.pairtype import extendabletype


class Node(object):
    # Allows using __extend__ to extend the type
    __metaclass__ = extendabletype


@attributes([
    Attribute(name="operator"),
    Attribute(name="left"),
    Attribute(name="right"),
])
class BinaryOperation(Node):
    def __init__(self):
        assert self.operator in ("+", "-", "!=") # for now

@attributes([
    Attribute(name="name"),
    Attribute(name="vtype"),
    Attribute(name="value"),
])
class VariableDeclaration(Node):
    def __init__(self):
        assert self.vtype == "INT32"

@attributes([Attribute(name="value")])
class Int32(Node):
    def __init__(self):
        assert isinstance(self.value, int)
        assert -2**32 < self.value <= 2**32-1

@attributes([Attribute(name="name")])
class Variable(Node):
    def __init__(self):
        pass

@attributes([Attribute(name="operator"), Attribute(name="variable")])
class PostOperation(Node):
    def __init__(self):
        assert self.operator in ("++", "--")

@attributes([Attribute(name="left"), Attribute(name="right")])
class Assignment(Node):
    def __init__(self):
        assert isinstance(self.left, Variable)
