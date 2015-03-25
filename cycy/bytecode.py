from characteristic import Attribute, attributes


LOAD_CONST = 1
BINARY_NEQ = 2


NAMES = {
    1: "LOAD_CONST",
    2: "BINARY_NEQ",
}

# bytecode => (has_arg, )
META = {
    LOAD_CONST: (True, ),
    BINARY_NEQ: (False, ),
}

BINARY_OPERATION_BYTECODE = {
    "!=": BINARY_NEQ,
}


@attributes(
    [
        Attribute(name="instructions", exclude_from_repr=True),
        Attribute(name="name"),
        Attribute(name="constants"),
        Attribute(name="number_of_variables"),
    ],
    apply_with_init=False,
)
class Bytecode(object):
    def __init__(self, instructions, name, constants, number_of_variables):
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
            next_offset = offset + 1
            byte_code = self.instructions[offset]
            arg = None

            has_arg, = META[byte_code]
            if has_arg:
                arg = self.instructions[next_offset]
                next_offset += 1

            yield (offset, byte_code, arg)
            offset = next_offset

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
