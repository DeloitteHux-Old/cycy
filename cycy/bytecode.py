from characteristic import Attribute, attributes


LOAD_CONST = 1
BINARY_NEQ = 2
PUTC       = 3


NAMES = {
    LOAD_CONST: "LOAD_CONST",
    BINARY_NEQ: "BINARY_NEQ",
    PUTC: "PUTC",
}


BINARY_OPERATION_BYTECODE = {
    "!=": BINARY_NEQ,
}


NO_ARG = -42


@attributes(
    [
        Attribute(name="instructions", exclude_from_repr=True),
        Attribute(name="name"),
        Attribute(name="constants", exclude_from_repr=True),
        Attribute(name="number_of_variables"),
    ],
    apply_with_init=False,
)
class Bytecode(object):
    def __init__(self, instructions, constants, number_of_variables, name):
        """
        :argument list instructions: the list of bytecode instructions
        :argument list constants: the collection of constants indexed
            into by the instructions
        :argument int number_of_variables: yeah, that
        :argument str name: an optional source-file name

        """

        self.instructions = instructions
        self.name = name
        self.constants = constants
        self.number_of_variables = number_of_variables

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
