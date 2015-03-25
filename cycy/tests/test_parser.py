from unittest import TestCase

from cycy.parser import parse
from cycy.parser.ast import (
    Array,
    ArrayDereference,
    Assignment,
    BinaryOperation,
    Block,
    Char,
    Function,
    Int32,
    PostOperation,
    ReturnStatement,
    Variable,
    VariableDeclaration,
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

    def test_char_literal(self):
        self.assertEqual(
            parse("'c'"),
            Char(value='c')
        )

    def test_string_literal(self):
        self.assertEqual(
            parse('"foo"'),
            Array(value=[Char(value='f'), Char(value='o'), Char(value='o'), Char(value=chr(0))])
        )

    def test_array_deference(self):
        self.assertEqual(
            parse("array[4]"),
            ArrayDereference(array=Variable(name="array"), index=Int32(value=4))
        )

    def test_return_statement(self):
        self.assertEqual(
            parse("return 0;"),
            ReturnStatement(value=Int32(value=0))
        )

    def test_main_function(self):
        self.assertEqual(
            parse("int main(void) { return 0; }"),
            Function(
                return_type="INT32",
                name="main",
                params=[],
                body=Block([
                        ReturnStatement(value=Int32(value=0))
                ])
            )
        )
