from rpython.rlib import streamio

from cycy import __version__
from cycy.exceptions import CyCyError
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

            if repl_input.startswith("##"):
                command_and_argument = repl_input[2:].strip().split(" ", 1)
                command = command_and_argument.pop(0)
                if command_and_argument:
                    repl_input = command_and_argument.pop()
                else:
                    repl_input = ""

                if command == "dump":
                    new_functions = self.interpreter.compile(repl_input)
                    for function_name in new_functions:
                        self.dump(function_name)
                        self.stdout.write("\n")
                elif command == "compile":
                    source_file = streamio.open_file_as_stream(repl_input)
                    self.interpreter.compile(source_file.readall())
                    source_file.close()
                else:
                    self.stderr.write("Unknown command: '%s'\n" % (command,))
            else:
                self.interpret(repl_input)
                self.stdout.write("\n")

    def interpret(self, source):
        # XXX: multiple lines, and pass stdin / stdout / stderr down
        try:
            return_value = self.interpreter.interpret([source])
        except CyCyError as error:
            self.stdout.write(error.rstr())
            self.stdout.write("\n")
        else:
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
