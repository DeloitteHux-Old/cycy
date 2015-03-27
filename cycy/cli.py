"""
Usage
=====

cycy [options] [C_FILE ...]


Options
-------

"""

from textwrap import dedent
import os

from characteristic import Attribute, attributes

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
        source_string=None,
    ):
        if source_files is None:
            source_files = []

        self.action = action
        self.cycy = cycy
        self.failure = failure
        self.source_files = source_files
        self.source_string = source_string


def parse_args(args):
    source_string = None
    source_files = []
    include_paths = []

    arguments = iter(args)
    for argument in arguments:
        if argument in ("-h", "--help"):
            return CommandLine(action=print_help)

        if argument == "-I":
            try:
                include_paths.append(next(arguments))
            except StopIteration:
                return CommandLine(
                    action=print_help, failure="-I expects an argument",
                )
        elif argument == "-c":
            try:
                source_string = next(arguments)
            except StopIteration:
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

    cycy = CyCy(environment=Environment(include_paths=include_paths))
    if source_files or source_string:
        return CommandLine(
            action=run_source,
            cycy=cycy,
            source_files=source_files,
            source_string=source_string,
        )
    else:
        return CommandLine(action=run_repl, cycy=cycy)


def print_help(command_line):
    exit_status = os.EX_OK

    if command_line.failure:
        os.write(2, command_line.failure)
        os.write(2, "\n")
        exit_status = os.EX_USAGE

    os.write(2, __doc__)
    return exit_status


def run_source(command_line):
    cycy = command_line.cycy

    if command_line.source_string:
        w_exit_status = cycy.interpret_source(command_line.source_string)
    else:
        w_exit_status = cycy.interpret(command_line.source_files)

    return w_exit_status.rint()


def run_repl(command_line):
    REPL().run()
    return os.EX_OK
