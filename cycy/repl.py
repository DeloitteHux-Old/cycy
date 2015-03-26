import os

from rpython.rlib import streamio

from cycy import __version__
from cycy.interpreter import CyCy


def _open(fd):
    base = streamio.DiskFile(fd)
    return streamio.BufferingInputStream(base)


class REPL(object):

    PROMPT = "CC-> "

    def __init__(self, stdin=None, stdout=None, stderr=None):
        # NOTE: This uses streamio, which by its own admission "isn't
        #       ready for general usage"
        self.stdin = stdin if stdin is not None else _open(fd=0)
        self.stdout = stdout if stdout is not None else _open(fd=1)
        self.stderr = stderr if stderr is not None else _open(fd=2)

        self.interpreter = CyCy()

    def run(self):
        self.show_banner()
        while True:
            self.stdout.write(self.PROMPT)
            program = self.stdin.readline()
            self.interpret(program)

    def interpret(self, source):
        # XXX: multiple lines, and pass stdin / stdout / stderr down
        return_value = self.interpreter.interpret_source(source=source)
        self.stdout.write(return_value.str())
        self.stdout.write("\n")

    def show_banner(self):
        self.stdout.write("CyCy %s\n\n" % (__version__,))


if __name__  == "__main__":
    REPL().run()
