"""
Execute ./cycy-c <filename>

"""

import sys

from rpython.rlib.streamio import open_file_as_stream
from rpython.jit.codewriter.policy import JitPolicy

from cycy.interpreter import interpret
from cycy.repl import REPL


def main(argv):
    if len(argv) == 1:
        REPL().run()
    elif len(argv) != 2:
        print __doc__
        return 1
    else:
        source_file = open_file_as_stream(argv[1])
        data = source_file.readall()
        source_file.close()
        interpret(data)
    return 0


def target(driver, args):
    return main, None


def jitpolicy(driver):
    return JitPolicy()
