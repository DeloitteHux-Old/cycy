"""
Execute ./cycy-c <filename>

"""

import sys

from rpython.jit.codewriter.policy import JitPolicy

from cycy.interpreter import CyCy
from cycy.repl import REPL

def main(argv):
    if len(argv) == 1:
        REPL().run()
        return 0

    print_help = False
    interpreter = CyCy()
    source_files = []

    for arg in argv[1:]:
        if arg == "--help" or arg == "-h":
            print_help = True
            break
        elif arg.startswith("-I"):
            interpreter.environment.add_include(arg[2:])
        else:
            source_files.append(arg)

    if print_help or len(argv) < 2:
        print __doc__
        return 1

    return interpreter.interpret(source_files).value


def target(driver, args):
    return main, None


def jitpolicy(driver):
    return JitPolicy()
