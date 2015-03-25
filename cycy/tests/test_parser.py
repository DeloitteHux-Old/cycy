from unittest import TestCase

from cycy.parser import parse
from cycy.parser.ast import (
    Assignment,
    BinaryOperation,
    Int32,
    PostOperation,
    Variable,
    VariableDeclaration
)

class TestParser(TestCase):
    def test_basic_ne(self):
        self.assertEqual(
            parse('2 != 3'),
            BinaryOperation(operator="!=", left=Int32(value=2), right=Int32(value=3))
        )

    def test_variable_declaration(self):
        self.assertEqual(
            parse('int i'),
            VariableDeclaration(name="i", vtype="INT32", value=None))

    def test_postincrement(self):
        self.assertEqual(
            parse("i++"),
            PostOperation(operator="++", variable=Variable(name="i"))
        )

    def test_assignment(self):
        self.assertEqual(
            parse("i = 0"),
            Assignment(left=Variable(name="i"), right=Int32(value=0))
        )
