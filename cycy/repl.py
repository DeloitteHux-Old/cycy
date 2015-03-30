import os

from rpython.rlib import streamio

from cycy import __version__
from cycy.interpreter import CyCy


def _open(fd):
    base = streamio.DiskFile(fd)
    return streamio.BufferingInputStream(base)


class REPL(object):

    PROMPT = "CC-> "

    def __init__(
        self,
        stdin=None,
        stdout=None,
        stderr=None,
        interpreter=None,
    ):
        if interpreter is None:
            interpreter = CyCy()

        # NOTE: This uses streamio, which by its own admission "isn't
        #       ready for general usage"
        self.stdin = stdin if stdin is not None else _open(fd=0)
        self.stdout = stdout if stdout is not None else _open(fd=1)
        self.stderr = stderr if stderr is not None else _open(fd=2)

        self.interpreter = interpreter

    def run(self):
        self.show_banner()
        while True:
            self.stdout.write(self.PROMPT)

            try:
                repl_input = self.stdin.readline()
            except KeyboardInterrupt:
                self.stdout.write("\n")
                continue

            if not repl_input:
                return
            elif not repl_input.strip():
                continue

            if repl_input.startswith("dump "):
                repl_input = repl_input[5:]
                newly_compiled_functions = self.interpreter.compile(repl_input)
                for function_name in newly_compiled_functions:
                    self.dump(function_name)
                    self.stdout.write("\n")
            else:
                self.interpret(repl_input)
                self.stdout.write("\n")

    def interpret(self, source):
        # XXX: multiple lines, and pass stdin / stdout / stderr down
        return_value = self.interpreter.interpret(source)
        if return_value is not None:
            self.stdout.write(return_value.str())

    def dump(self, function_name):
        """
        Pretty-dump the bytecode for the function with the given name.

        """

        self.stdout.write(function_name)
        self.stdout.write("\n")
        self.stdout.write("-" * len(function_name))
        self.stdout.write("\n\n")

        byte_code = self.interpreter.compiled_functions[function_name]
        self.stdout.write(byte_code.dump())
        self.stdout.write("\n")

    def show_banner(self):
        self.stdout.write("CyCy %s\n\n" % (__version__,))


if __name__  == "__main__":
    REPL().run()
