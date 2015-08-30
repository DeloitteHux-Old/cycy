"""
Usage
=====

cycy [options] [C_FILE ...]


Options
-------

-h, --help       display this help message
--version        display version information


-c PROGRAM       execute the given program, passed in
                 as a string (terminates option list)
-I, --include    specify an additional include path to search within

"""

import os

from characteristic import Attribute, attributes
from rpython.rlib.streamio import open_file_as_stream

from cycy import __version__
from cycy.interpreter import CyCy
from cycy.environment import Environment
from cycy.repl import REPL


@attributes(
    [
        Attribute(name="action"),
        Attribute(name="cycy"),
        Attribute(name="failure"),
        Attribute(name="source_files"),
        Attribute(name="source_string"),
    ],
    apply_with_init=False,
)
class CommandLine(object):
    """
    The parsed results of a command line.

    """

    def __init__(
        self,
        action,
        cycy=None,
        failure="",
        source_files=None,
        source_string="",
    ):
        if source_files is None:
            source_files = []

        self.action = action
        self.cycy = cycy
        self.failure = failure
        self.source_files = source_files
        self.source_string = source_string


def parse_args(args):
    source_string = ""
    source_files = []
    include_paths = []

    arguments = iter(args)
    for argument in arguments:
        if argument in ("-h", "--help"):
            return CommandLine(action=print_help)
        if argument == "--version":
            return CommandLine(action=print_version)

        if argument in ("-I", "--include"):
            try:
                include_paths.append(next(arguments))
            except StopIteration:
                return CommandLine(
                    action=print_help, failure="-I expects an argument",
                )
        elif argument == "-c":
            source = []  # this is the simplest valid RPython currently
            for argument in arguments:
                source.append(argument)
            source_string = " ".join(source)

            if not source_string:
                return CommandLine(
                    action=print_help, failure="-c expects an argument",
                )
        elif not argument.startswith("-"):
            source_files.append(argument)
        else:
            return CommandLine(
                action=print_help,
                failure="Unknown argument %s" % (argument,),
            )

    environment = Environment.with_directories(directories=include_paths)
    cycy = CyCy(environment=environment)
    if source_files or source_string:
        return CommandLine(
            action=run_source,
            cycy=cycy,
            source_files=source_files,
            source_string=source_string,
        )
    else:
        return CommandLine(action=run_repl, cycy=cycy)


def run_source(command_line):
    cycy = command_line.cycy

    sources = []
    source_string = command_line.source_string
    if source_string:
        sources.append(source_string)
    else:
        for source_path in command_line.source_files:
            source_file = open_file_as_stream(source_path)
            sources.append(source_file.readall())
            source_file.close()

    w_exit_status = cycy.interpret(sources)
    if w_exit_status is None:  # internal error during interpret
        return 1
    return w_exit_status.rint()


def run_repl(command_line):
    REPL(interpreter=command_line.cycy).run()
    return os.EX_OK


def print_help(command_line):
    exit_status = os.EX_OK

    if command_line.failure:
        os.write(2, command_line.failure)
        os.write(2, "\n")
        exit_status = os.EX_USAGE

    os.write(2, __doc__)
    return exit_status


def print_version(command_line):
    os.write(2, "CyCy %s\n" % (__version__,))
    return os.EX_OK
