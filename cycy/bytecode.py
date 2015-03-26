from characteristic import Attribute, attributes


LOAD_CONST = 1
BINARY_NEQ = 2
PUTC       = 3
BINARY_LEQ = 4
RETURN     = 5
STORE_VARIABLE = 6
LOAD_VARIABLE  = 7

JUMP             = 8
JUMP_IF_NOT_ZERO = 9

CALL = 10
BINARY_ADD = 11
BINARY_SUB = 12
DEREFERENCE = 13

NAMES = {
    LOAD_CONST: "LOAD_CONST",
    BINARY_NEQ: "BINARY_NEQ",
    PUTC: "PUTC",
    BINARY_LEQ: "BINARY_LEQ",
    RETURN: "RETURN",
    STORE_VARIABLE: "STORE_VARIABLE",
    LOAD_VARIABLE: "LOAD_VARIABLE",
    JUMP_IF_NOT_ZERO: "JUMP_IF_NOT_ZERO",
    JUMP: "JUMP",
    CALL: "CALL",
    BINARY_ADD: "BINARY_ADD",
    BINARY_SUB: "BINARY_SUB",
    DEREFERENCE: "DEREFERENCE"
}


BINARY_OPERATION_BYTECODE = {
    "!=": BINARY_NEQ,
    "<=": BINARY_LEQ,
    "+": BINARY_ADD,
    "-": BINARY_SUB,
}


NO_ARG = -42


@attributes(
    [
        Attribute(name="instructions", exclude_from_repr=True),
        Attribute(name="name"),
        Attribute(name="arguments"),
        Attribute(name="constants", exclude_from_repr=True),
        Attribute(name="variables", exclude_from_repr=True),
    ],
    apply_with_init=False,
)
class Bytecode(object):
    """
    The bytecode, man.

    .. attribute:: instructions
    .. attribute:: arguments

        a tuple of argument names

    .. attribute:: constants

        inherited from the :class:`cycy.compiler.Context` that produced this
        bytecode

    .. attribute:: variables

        a mapping between variable names (:class:`str`\ s) and the
        indices in an array that they should be assigned to

    .. attribute:: name

        an optional :class:`str` which is the source-file name

    """

    def __init__(self, instructions, arguments, constants, variables, name):
        self.instructions = instructions
        self.name = name
        self.arguments = arguments
        self.constants = constants
        self.variables = variables

    def __iter__(self):
        """Yield (offset, byte_code, arg) tuples.

        The `byte_code` will be one of the constants defined above,
        and `arg` may be None. `byte_code` and `arg` will be ints.
        """
        offset = 0
        while offset < len(self.instructions):
            byte_code = self.instructions[offset]
            arg = self.instructions[offset + 1]
            if arg is NO_ARG:
                arg = None

            yield (offset, byte_code, arg)
            offset += 2

    def dump(self):
        lines = []

        for offset, byte_code, arg in self:
            name = NAMES[byte_code]
            if arg is None:
                arg = ""

            line = "{offset:d} {name} {arg}".format(
                offset=offset,
                name=name,
                arg=arg,
            )
            lines.append(line.strip())

        return "\n".join(lines)


def cleaned(humanish_bytecode):
    """
    Take bytecode in a humanish format::

        LOAD_CONST 0
        DO_STUFF 2 3  # do cool thangs

    and clean comments and whitespace.

    """

    return humanish_bytecode
