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
JUMP_IF_ZERO     = 14

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
    DEREFERENCE: "DEREFERENCE",
    JUMP_IF_ZERO: "JUMP_IF_ZERO",
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
        Attribute(name="tape"),
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

    .. attribute:: tape
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

    def __init__(self, tape, arguments, constants, variables, name):
        self.tape = tape
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
        while offset < len(self.tape):
            byte_code = self.tape[offset]
            arg = self.tape[offset + 1]

            yield (offset, byte_code, arg)
            offset += 2

    def dump(self, pretty=True):
        lines = []

        for offset, byte_code, arg in self:
            name = NAMES[byte_code]
            str_arg = ""
            if arg != NO_ARG:
                str_arg = "%s" % arg

            line = "%s %s %s" % (str(offset), name, str_arg)
            if pretty:
                if byte_code in (LOAD_CONST, CALL):
                    line += " => " + self.constants[arg].dump()
                elif byte_code in (STORE_VARIABLE, LOAD_VARIABLE):
                    for name, index in list(self.variables.items()):
                        if index == arg:
                            line += " => " + name
                            break
                elif byte_code == RETURN:
                    if arg:
                        line += " (top of stack)"
                    else:
                        line += " (void return)"
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
