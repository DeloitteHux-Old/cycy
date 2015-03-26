from unittest import TestCase

from cycy.parser import parse
from cycy.parser.ast import (
    Array,
    ArrayDereference,
    Assignment,
    BinaryOperation,
    Block,
    Call,
    Char,
    Function,
    Int32,
    PostOperation,
    ReturnStatement,
    Variable,
    VariableDeclaration,
)

class TestParser(TestCase):
    def function_wrap(self, source):
        return "int main(void) { %s }" % source

    def function_wrap_node(self, node):
        return Function(
            return_type="INT32",
            name="main",
            params=[],
            body=Block([node])
)

    def test_basic_ne(self):
        self.assertEqual(
            parse(self.function_wrap('2 != 3;')),
            self.function_wrap_node(
                BinaryOperation(operator="!=", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('int i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype="INT32", value=None)
            )
        )

    def test_postincrement(self):
        self.assertEqual(
            parse(self.function_wrap("i++;")),
            self.function_wrap_node(
                PostOperation(operator="++", variable=Variable(name="i"))
            )
        )

    def test_assignment(self):
        self.assertEqual(
            parse(self.function_wrap("i = 0;")),
            self.function_wrap_node(
                Assignment(left=Variable(name="i"), right=Int32(value=0))
            )
        )

    def test_char_literal(self):
        self.assertEqual(
            parse(self.function_wrap("'c';")),
            self.function_wrap_node(
                Char(value='c')
            )
        )

    def test_string_literal(self):
        self.assertEqual(
            parse(self.function_wrap('"foo";')),
            self.function_wrap_node(
                Array(value=[Char(value='f'), Char(value='o'), Char(value='o'), Char(value=chr(0))])
            )
        )

    def test_array_deference(self):
        self.assertEqual(
            parse(self.function_wrap("array[4];")),
            self.function_wrap_node(
                ArrayDereference(array=Variable(name="array"), index=Int32(value=4))
            )
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

    def test_function_call(self):
        self.assertEqual(
            parse(self.function_wrap("putc(string);")),
            self.function_wrap_node(
                Call(
                    name="putc",
                    args=[Variable(name="string")]
                )
            )
        )
