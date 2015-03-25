from characteristic import Attribute, attributes


class Node(object):
    pass


@attributes([
    Attribute(name="operand"),
    Attribute(name="left"),
    Attribute(name="right"),
])
class BinaryOperation(Node):
    def __init__(self):
        assert self.operand in ("+", "-", "!=") # for now

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

@attributes([Attribute(name="operand"), Attribute(name="variable")])
class PostOperation(Node):
    def __init__(self):
        assert self.operand in ("++", "--")

@attributes([Attribute(name="left"), Attribute(name="right")])
class Assignment(Node):
    def __init__(self):
        assert isinstance(self.left, Variable)
