class Node(object):
    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.__dict__ == other.__dict__
        )

    def __ne__(self, other):
        return not self == other

class BinaryOperation(Node):
    def __init__(self, operand, left, right):
        assert operand in ("+", "-") # for now
        self.operand = operand
        self.left = left
        self.right = right

class Int32(Node):
    def __init__(self, value):
        assert isinstance(value, int)
        assert -2**32 < value <= 2**32-1
        self.value = value
