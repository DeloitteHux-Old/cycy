from rpython.rlib import streamio

from cycy import __version__
from cycy.interpreter import CyCy
from cycy.parser.core import IncrementalParser


class REPL(object):

    PROMPT = "CC-> "
    INPUT_IN_PROGRESS_PROMPT = " ... "

    def __init__(self, interpreter=None):
        if interpreter is None:
            interpreter = CyCy(parser=IncrementalParser())

        self.interpreter = interpreter
        self.stdin = interpreter.stdin
        self.stdout = interpreter.stdout
        self.stderr = interpreter.stderr
        self.compiler = interpreter.compiler
        self.parser = interpreter.parser

    @property
    def prompt(self):
        if self.interpreter.parser.input_in_progress:
            return self.INPUT_IN_PROGRESS_PROMPT
        return self.PROMPT

    def run(self):
        self.show_banner()
        while True:
            self.stdout.write(self.prompt)

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
                    ast = self.parser.parse(repl_input)
                    new_functions = self.compiler.compile(ast)
                    for function_name in new_functions:
                        self.dump(function_name)
                        self.stdout.write("\n")
                elif command == "compile":
                    source_file = streamio.open_file_as_stream(repl_input)
                    ast = self.parser.parse(source_file.readall())
                    self.compiler.compile(ast)
                    source_file.close()
                else:
                    self.stderr.write("Unknown command: '%s'\n" % (command,))
            else:
                self.interpret(repl_input)
                self.stdout.write("\n")

    def interpret(self, source):
        return_value = self.interpreter.interpret([source])
        if return_value is not None:
            self.stdout.write(return_value.str())

    def dump(self, function_name):
        """
        Pretty-dump the bytecode for the function with the given name.

        """

        assert isinstance(function_name, str)
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
