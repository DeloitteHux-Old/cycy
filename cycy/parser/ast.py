from characteristic import Attribute, attributes


class Node(object):
    pass


@attributes([
    Attribute(name="operand"),
    Attribute(name="left"),
    Attribute(name="right"),
])
class BinaryOperation(Node):
    def __init__(self, operand, left, right):
        assert operand in ("+", "-", "!=") # for now
        self.operand = operand
        self.left = left
        self.right = right

@attributes([Attribute(name="value")])
class Int32(Node):
    def __init__(self):
        assert isinstance(self.value, int)
        assert -2**32 < self.value <= 2**32-1
