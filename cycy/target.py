import sys

from rpython.jit.codewriter.policy import JitPolicy

from cycy.cli import parse_args
from cycy.interpreter import CyCy
from cycy.repl import REPL


def main(argv):
    command_line = parse_args(argv[1:])
    exit_status = command_line.action(command_line)
    return exit_status


def target(driver, args):
    return main, None


def jitpolicy(driver):
    return JitPolicy()
