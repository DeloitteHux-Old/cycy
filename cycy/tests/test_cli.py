from unittest import TestCase

from cycy import cli
from cycy.interpreter import CyCy
from cycy.parser import preprocessor
from cycy.parser.core import Parser


class TestArgumentParsing(TestCase):
    def test_run_source_files(self):
        self.assertEqual(
            cli.parse_args(["-I", "a/include", "-I", "b/include", "file.c"]),
            cli.CommandLine(
                action=cli.run_source,
                source_files=["file.c"],
                cycy=CyCy(
                    parser=Parser(
                        preprocessor=preprocessor.with_directories(
                            ["a/include", "b/include"],
                        ),
                    ),
                ),
            ),
        )

    def test_run_source_string(self):
        self.assertEqual(
            cli.parse_args(["-I", "a/include", "-c", "int main (void) {}"]),
            cli.CommandLine(
                action=cli.run_source,
                source_string="int main (void) {}",
                cycy=CyCy(
                    parser=Parser(
                        preprocessor=preprocessor.with_directories(
                            ["a/include"],
                        ),
                    ),
                ),
            ),
        )

    def test_run_repl(self):
        self.assertEqual(
            cli.parse_args([]),
            cli.CommandLine(action=cli.run_repl, cycy=CyCy()),
        )

    def test_unknown_arguments_causes_print_help(self):
        self.assertEqual(
            cli.parse_args(["-I", "stuff/include", "--foobar"]),
            cli.CommandLine(
                action=cli.print_help,
                failure="Unknown argument --foobar",
            ),
        )

    def test_argument_with_missing_argument(self):
        self.assertEqual(
            cli.parse_args(["-I"]),
            cli.CommandLine(
                action=cli.print_help,
                failure="-I expects an argument",
            ),
        )

    def test_help(self):
        self.assertEqual(
            cli.parse_args(["-h"]),
            cli.CommandLine(action=cli.print_help),
        )
        self.assertEqual(
            cli.parse_args(["--help"]),
            cli.CommandLine(action=cli.print_help),
        )

    def test_version(self):
        self.assertEqual(
            cli.parse_args(["--version"]),
            cli.CommandLine(action=cli.print_version),
        )
