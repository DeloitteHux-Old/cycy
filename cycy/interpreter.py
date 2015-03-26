import os

from cycy import bytecode
from cycy.parser.sourceparser import parse


class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def run(self, byte_code):
        pc = 0
        while pc < len(byte_code.instructions):
            opcode = byte_code.instructions[pc]
            arg = byte_code.instructions[pc + 1]
            pc += 2

            if opcode == bytecode.PUTC:
                value = byte_code.constants[arg]
                os.write(1, chr(value))
                # TODO: error handling?


def interpret(source):
    from cycy import compiler
    ast = parse(source)
    byte_code = compiler.compile(ast=ast)
    CyCy().run(byte_code=byte_code)


class WrappedThing(object):
    pass


class WrappedInt32(WrappedThing):
    # TODO: different sizes of ints :\

    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value
