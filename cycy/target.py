"""
Execute ./cycy-c <filename>

"""

import sys

from rpython.rlib.streamio import open_file_as_stream

from cycy.interpreter import interpret


def main(argv):
    if len(argv) != 2:
        print __doc__
        return 1
    source_file = open_file_as_stream(argv[1])
    data = source_file.readall()
    source_file.close()
    interpret(data)
    return 0


def target(driver, args):
    return main, None
