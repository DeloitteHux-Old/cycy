from textwrap import dedent
from unittest import TestCase

from cycy import compiler
from cycy.bytecode import cleaned
from cycy.parser.sourceparser import parse


class TestCompiler(TestCase):
    def assertCompiles(self, source, to=None):
        """
        Assert the given source code compiles, with an optional expected
        output.

        """

        bytecode = compiler.compile(ast=parse(source))
        expected = dedent(cleaned(to).strip("\n")).strip("\n")
        self.assertEqual(bytecode.dump(), expected)

    def test_basic_neq(self):
        self.assertCompiles(
            "2 != 3", """
            0 LOAD_CONST 0
            2 LOAD_CONST 1
            4 BINARY_NEQ
            """
        )
