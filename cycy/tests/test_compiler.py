from textwrap import dedent
from unittest import TestCase, skip

from cycy import compiler
from cycy.bytecode import cleaned
from cycy.parser.sourceparser import parse


class TestCompiler(TestCase):
    def assertCompiles(self, source, to=None):
        """
        Assert the given source code compiles, with an optional expected
        output.

        """

        program = parse(source)
        main_func_ast = next(func for func in program.functions() if func.name == "main")
        bytecode = compiler.compile(main_func_ast)
        expected = dedent(cleaned(to).strip("\n")).strip("\n")
        self.assertEqual(bytecode.dump(), expected)

    def test_basic_neq(self):
        self.assertCompiles(
            "int main(void) { 2 != 3; }", """
            0 LOAD_CONST 0
            2 LOAD_CONST 1
            4 BINARY_NEQ
            """
        )

    def test_char_array(self):
        self.assertCompiles(
            "int main(void) { const char* foo = \"foo\"; }", """
            0 LOAD_CONST 0
            2 STORE_VARIABLE 0
            """
        )
