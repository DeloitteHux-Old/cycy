from textwrap import dedent
from unittest import TestCase

from cycy import compiler
from cycy.bytecode import cleaned
from cycy.interpreter import CyCy


class TestCompilerIntegration(TestCase):
    def setUp(self):
        self.compiler = compiler.Compiler()

    def assertCompiles(self, source, to=None):
        """
        The given source code is successfully compiled, optionally to the
        provided expected output.

        """

        ast = CyCy().parse(source="int main(void) { " + source + "}")
        self.compiler.compile(ast)
        main = self.compiler.constants[self.compiler.functions["main"]]
        expected = dedent(cleaned(to).strip("\n")).strip("\n")
        self.assertEqual(main.bytecode.dump(pretty=False), expected)

    def test_basic_neq(self):
        self.assertCompiles(
            "2 != 3;", """
            0 LOAD_CONST 0
            2 LOAD_CONST 1
            4 BINARY_NEQ
            """
        )

    def test_char_array(self):
        self.assertCompiles(
            "const char* foo = \"foo\";", """
            0 LOAD_CONST 0
            2 STORE_VARIABLE 0
            """
        )

    def test_array_dereference(self):
        self.assertCompiles(
            "const char* foo = \"foo\"; foo[3];", """
            0 LOAD_CONST 0
            2 STORE_VARIABLE 0
            4 LOAD_CONST 1
            6 LOAD_VARIABLE 0
            8 DEREFERENCE
            """
        )
