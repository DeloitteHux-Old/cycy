import os

from cycy import bytecode, compiler
from cycy.objects import W_Char
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
                assert isinstance(value, W_Char)
                os.write(1, value.str())
                # TODO: error handling?


def interpret(source):
    ast = parse(source)
    byte_code = compiler.compile(ast=ast)
    CyCy().run(byte_code=byte_code)
