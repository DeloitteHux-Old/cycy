from unittest import TestCase

from cycy import cli
from cycy.environment import Environment
from cycy.interpreter import CyCy


class TestArgumentParsing(TestCase):
    def test_help(self):
        self.assertEqual(
            cli.parse_args(["-h"]),
            cli.CommandLine(action=cli.print_help),
        )
        self.assertEqual(
            cli.parse_args(["--help"]),
            cli.CommandLine(action=cli.print_help),
        )

    def test_run_source_files(self):
        self.assertEqual(
            cli.parse_args(["-I", "a/include", "-I", "b/include", "file.c"]),
            cli.CommandLine(
                action=cli.run_source,
                source_files=["file.c"],
                cycy=CyCy(
                    environment=Environment(
                        include_paths=["a/include", "b/include"],
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
                    environment=Environment(include_paths=["a/include"]),
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
