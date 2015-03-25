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
        Attribute(name="bytes", exclude_from_repr=True),
        Attribute(name="name"),
        Attribute(name="constants"),
        Attribute(name="number_of_variables"),
    ],
    apply_with_init=False,
)
class Bytecode(object):
    def __init__(self, bytes, name, constants, number_of_variables):
        self.bytes = bytes
        self.name = name
        self.constants = constants
        self.number_of_variables = number_of_variables

    def dump(self):
        lines = []
        skip = 0
        for i, byte in enumerate(self.bytes):
            if skip > 0:
                skip -= 1
                continue

            code = ord(byte)
            name = NAMES[code]
            has_arg, = META[code]
            if has_arg:
                arg = self.bytes[i + 1]  # TODO: ugh
                arg = ord(arg)  # TODO: is arg always 1 byte?
                line = "{offset:d} {name} {arg}".format(
                    offset=i,
                    name=name,
                    arg=arg,
                )
                skip = 1
            else:
                line = "{offset:d} {name}".format(
                    offset=i,
                    name=name,
                )

            lines.append(line)

        return "\n".join(lines)


def cleaned(humanish_bytecode):
    """
    Take bytecode in a humanish format::

        LOAD_CONST 0
        DO_STUFF 2 3  # do cool thangs

    and clean comments and whitespace.

    """

    return humanish_bytecode
