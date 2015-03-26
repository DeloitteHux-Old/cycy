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
    def __init__(self, name, vtype, value=None):
        self.name = name
        self.vtype = vtype
        self.value = value

@attributes([Attribute(name="value")], apply_with_init=False)
class Int32(Node):
    def __init__(self, value):
        self.value = value

@attributes([Attribute(name="value")], apply_with_init=False)
class Double(Node):
    def __init__(self, value):
        self.value = value

@attributes([Attribute(name="value")], apply_with_init=False)
class String(Node):
    def __init__(self, value):
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
    char_escapes = {"n": "\n"}

    def __init__(self, value):
        if len(value) == 2 and value[0] == "\\":
            value = self.char_escapes.get(value[1], value[1])
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

@attributes(
    [
        Attribute(name="return_type"),
        Attribute(name="name"),
        Attribute(name="params"),
        Attribute(name="body"),
        Attribute(name="_prototype")
    ],
    apply_with_init=False
)
class Function(Node):
    def __init__(self, return_type=None, name=None, params=None, body=None, prototype=False):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body
        self._prototype = prototype

    def prototype(self):
        return self._prototype


@attributes(
    [
        Attribute(name="statements")
    ],
    apply_with_init=False
)
class Block(Node):
    def __init__(self, statements):
        self.statements = statements

@attributes(
    [
        Attribute(name="name"),
        Attribute(name="args"),
    ],
    apply_with_init=False
)
class Call(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Null(Node):
    # This isn't actually a type in C, but we don't support macros, or pointers
    # yet which are required to #define NULL (void*)0
    def __eq__(self, other):
        if isinstance(other, Null):
            return True
        return False

@attributes(
    [
        Attribute(name="condition"),
        Attribute(name="body")
    ],
    apply_with_init=False
)
class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

@attributes(
    [
        Attribute(name="units")
    ],
    apply_with_init=False
)
class Program(Node):
    def __init__(self, units):
        self.units = units

    def add_unit(self, unit):
        self.units.append(unit)

    def functions(self):
        return [unit for unit in self.units if not unit.prototype()]


@attributes(
    [
        Attribute(name="base_type"),
        Attribute(name="const"),
        Attribute(name="unsigned"),
        Attribute(name="length"),
        Attribute(name="reference"),
    ],
    apply_with_init=False
)
class Type(Node):
    def __init__(self, base=None, const=False, unsigned=False, reference=None):
        if base == 'char':
            self.base_type = 'int'
            self.length = 8
        elif base == 'short':
            self.base_type = 'int'
            self.length = 16
        elif base == 'int' or base == 'long':
            self.base_type = 'int'
            self.length = 32
        elif base == 'long long':
            self.base_type = 'int'
            self.length = 64
        elif base == 'float':
            self.base_type = 'float'
            self.length = 32
        elif base == 'double':
            self.base_type = 'float'
            self.length = 64
        elif base == 'long double':
            self.base_type = 'float'
            self.length = 80
        else:
            self.base_type = base
            self.length = -1

        self.const = const
        self.unsigned = unsigned
        self.reference = reference
