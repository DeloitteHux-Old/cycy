from cycy import compiler
from cycy.parser.sourceparser import parse


class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def run(self, bytecode):
        pass


def interpret(source):
    print "Hello, world!"
    return

    bytecode = compiler.Context.to_bytecode(parse(source.getContent()))
    CyCy().run(bytecode)
