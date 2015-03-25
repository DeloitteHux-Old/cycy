from cycy import compiler
from cycy.parser.sourceparser import parse


class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def run(self, bytecode):
        pass


def interpret(source):
    ast = parse(source)
    bytecode = compiler.compile(ast=ast)
    CyCy().run(bytecode=bytecode)
