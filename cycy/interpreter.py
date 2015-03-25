import sys

from cycy import bytecode
from cycy import compiler
from cycy.parser.sourceparser import parse


class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def run(self, byte_code):
        pc = 0
        while pc < len(byte_code.instructions):
            opcode = byte_code.instructions[pc]
            pc += 1

            if opcode == bytecode.PUTC:
                arg = byte_code.instructions[pc]
                pc += 1
                value = byte_code.constants[arg]
                sys.stdout.write(chr(value))


def interpret(source):
    ast = parse(source)
    byte_code = compiler.compile(ast=ast)
    CyCy().run(byte_code=byte_code)
