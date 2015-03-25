from unittest import TestCase

from cycy.parser import parse
from cycy.parser.ast import BinaryOperation, Int32, VariableDeclaration

class TestParser(TestCase):
    def test_basic_ne(self):
        self.assertEqual(
            parse('2 != 3'),
            BinaryOperation(operand="!=", left=Int32(value=2), right=Int32(value=3))
        )

    def test_variable_declaration(self):
        self.assertEqual(
            parse('int i'),
            VariableDeclaration(name="i", vtype="INT32", value=None))
