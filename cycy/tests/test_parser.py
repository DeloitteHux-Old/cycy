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
    Null,
    PostOperation,
    Program,
    ReturnStatement,
    String,
    Variable,
    VariableDeclaration,
    While,
    Type,
)

class TestParser(TestCase):
    def function_wrap(self, source):
        return "int main(void) { %s }" % source

    def function_wrap_node(self, node):
        return Program([Function(
            return_type=Type(base="int"),
            name="main",
            params=[],
            body=Block([node])
        )])

    def test_basic_ne(self):
        self.assertEqual(
            parse(self.function_wrap('2 != 3;')),
            self.function_wrap_node(
                BinaryOperation(operator="!=", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_basic_eq(self):
        self.assertEqual(
            parse(self.function_wrap('2 == 3;')),
            self.function_wrap_node(
                BinaryOperation(operator="==", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_basic_gt(self):
        self.assertEqual(
            parse(self.function_wrap('2 > 3;')),
            self.function_wrap_node(
                BinaryOperation(operator=">", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_basic_gte(self):
        self.assertEqual(
            parse(self.function_wrap('2 >= 3;')),
            self.function_wrap_node(
                BinaryOperation(operator=">=", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_basic_lt(self):
        self.assertEqual(
            parse(self.function_wrap('2 < 3;')),
            self.function_wrap_node(
                BinaryOperation(operator="<", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_basic_lte(self):
        self.assertEqual(
            parse(self.function_wrap('2 <= 3;')),
            self.function_wrap_node(
                BinaryOperation(operator="<=", left=Int32(value=2), right=Int32(value=3))
            )
        )

    def test_char_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('char i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="char"), value=None)
            )
        )
        var = Type(base="char")
        self.assertEqual( var.base_type, "int")
        self.assertEqual( var.length, 8)

    def test_int_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('int i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="int"), value=None)
            )
        )
        var = Type(base="int")
        self.assertEqual( var.base_type, "int")
        self.assertEqual( var.length, 32)

    def test_short_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('short i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="short"), value=None)
            )
        )
        var = Type(base="short")
        self.assertEqual( var.base_type, "int")
        self.assertEqual( var.length, 16)

    def test_string_variable_declaration(self):
        self.assertEqual(
            parse("int main(void) { const char* foo = \"foo\"; }"),
            self.function_wrap_node(
                VariableDeclaration(name="foo", vtype=Type(base="pointer", const=True, reference=Type(base="char")), value=String("foo"))
            )
        )

    def test_long_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('long i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="long"), value=None)
            )
        )
        var = Type(base="long")
        self.assertEqual( var.base_type, "int")
        self.assertEqual( var.length, 32)


    def test_long_long_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('long long i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="long long"), value=None)
            )
        )
        var = Type(base="long long")
        self.assertEqual( var.base_type, "int")
        self.assertEqual( var.length, 64)

    def test_float_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('float i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="float"), value=None)
            )
        )
        var = Type(base="float")
        self.assertEqual( var.base_type, "float")
        self.assertEqual( var.length, 32)

    def test_double_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('double i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="double"), value=None)
            )
        )
        var = Type(base="double")
        self.assertEqual( var.base_type, "float")
        self.assertEqual( var.length, 64)

    def test_long_double_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('long double i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="long double"), value=None)
            )
        )
        var = Type(base="long double")
        self.assertEqual( var.base_type, "float")
        self.assertEqual( var.length, 80)

    def test_variable_declaration_with_assignment(self):
        self.assertEqual(
            parse(self.function_wrap("int i = 0;")),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="int"), value=Int32(value=0))
            )
        )

    def test_pointer_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('int* i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="pointer", reference=Type(base="int")), value=None)
            )
        )
        self.assertEqual(
            parse(self.function_wrap('int *i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="pointer", reference=Type(base="int")), value=None)
            )
        )

    def test_pointer_to_pointer_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('char **argv;')),
            self.function_wrap_node(
                VariableDeclaration(name="argv", vtype=Type(base="pointer", reference=Type(base="pointer", reference=Type(base="char"))), value=None)
            )
        )

    def test_const_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('const int i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="int", const=True), value=None)
            )
        )

    def test_unsigned_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('unsigned int i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="int", unsigned=True), value=None)
            )
        )

    def test_unsigned_const_variable_declaration(self):
        self.assertEqual(
            parse(self.function_wrap('unsigned const int i;')),
            self.function_wrap_node(
                VariableDeclaration(name="i", vtype=Type(base="int", unsigned=True, const=True), value=None)
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

    def test_addition(self):
        self.assertEqual(
            parse(self.function_wrap("1 + 2;")),
            self.function_wrap_node(
                BinaryOperation(operator="+", left=Int32(value=1), right=Int32(value=2))
            )
        )

    def test_subtraction(self):
        self.assertEqual(
            parse(self.function_wrap("1 - 2;")),
            self.function_wrap_node(
                BinaryOperation(operator="-", left=Int32(value=1), right=Int32(value=2))
            )
        )

    def test_multiplication(self):
        self.assertEqual(
            parse(self.function_wrap("1 * 2;")),
            self.function_wrap_node(
                BinaryOperation(operator="*", left=Int32(value=1), right=Int32(value=2))
            )
        )

    def test_division(self):
        self.assertEqual(
            parse(self.function_wrap("1 / 2;")),
            self.function_wrap_node(
                BinaryOperation(operator="/", left=Int32(value=1), right=Int32(value=2))
            )
        )

    def test_modulus(self):
        self.assertEqual(
            parse(self.function_wrap("1 % 2;")),
            self.function_wrap_node(
                BinaryOperation(operator="%", left=Int32(value=1), right=Int32(value=2))
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
                String(value="foo")
            )
        )

    def test_array_dereference(self):
        self.assertEqual(
            parse(self.function_wrap("array[4];")),
            self.function_wrap_node(
                ArrayDereference(array=Variable(name="array"), index=Int32(value=4))
            )
        )

    def test_main_with_no_parameters(self):
        self.assertEqual(
            parse("int main(void) { return 0; }"),
            Program(units=[
                Function(
                    return_type=Type(base='int'),
                    name="main",
                    params=[],
                    body=Block([
                        ReturnStatement(value=Int32(value=0))
                    ])
                )
            ])
        )

    def test_main_with_multiple_parameters(self):
        self.assertEqual(
            parse("int main(int argc, char **argv, char **env) { return 0; }"),
            Program(units=[
                Function(
                    return_type=Type(base='int'),
                    name="main",
                    params=[
                        VariableDeclaration(name="argc", vtype=Type(base="int")),
                        VariableDeclaration(name="argv", vtype=Type(base="pointer", reference=Type(base="pointer", reference=Type(base="char")))),
                        VariableDeclaration(name="env", vtype=Type(base="pointer", reference=Type(base="pointer", reference=Type(base="char")))),
                        ],
                    body=Block([
                        ReturnStatement(value=Int32(value=0))
                    ])
                )
            ])
        )

    def test_function_arguments(self):
        self.assertEqual(
            parse("int puts(const char* string) { return 0; }"),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="puts",
                    params=[VariableDeclaration(name="string", vtype=Type(base="pointer", const=True, reference=Type(base="char")))],
                    body=Block([
                        ReturnStatement(value=Int32(value=0))
                    ])
                )
            ])
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

    def test_while_loop(self):
        self.assertEqual(
            parse(self.function_wrap("while (string[i] != NULL) { putc(string[i++]); }")),
            self.function_wrap_node(
                While(
                    condition=BinaryOperation(operator="!=",
                                              left=ArrayDereference(array=Variable(name="string"), index=Variable("i")),
                                              right=Null()),
                    body=Block([
                        Call(name="putc", args=[ArrayDereference(array=Variable("string"), index=PostOperation(operator="++", variable=Variable(name="i")))])
                    ])
                )
            )
        )

    def test_prototype_with_named_arguments(self):
        self.assertEqual(
            parse("int foo(int i, long l, double d, char *cp);"),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="foo",
                    params=[
                        VariableDeclaration(name="i", vtype=Type(base="int")),
                        VariableDeclaration(name="l", vtype=Type(base="long")),
                        VariableDeclaration(name="d", vtype=Type(base="double")),
                        VariableDeclaration(name="cp", vtype=Type(base="pointer", reference=Type(base="char"))),
                        ],
                    prototype=True,
                    )
                ])
            )

    def test_prototype_without_named_arguments(self):
        self.assertEqual(
            parse("int foo(int, long, double, char *);"),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="foo",
                    params=[
                        VariableDeclaration(name=None, vtype=Type(base="int")),
                        VariableDeclaration(name=None, vtype=Type(base="long")),
                        VariableDeclaration(name=None, vtype=Type(base="double")),
                        VariableDeclaration(name=None, vtype=Type(base="pointer", reference=Type(base="char"))),
                        ],
                    prototype=True,
                    )
                ])
            )

    def test_puts_function(self):
        self.assertEqual(
            parse("""
                int puts(const char * string) {
                    int i = 0;
                    while (string[i] != NULL) {
                        putc(string[i++]);
                    }
                    putc('\\n');
                    return i + 1;
                }
            """),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="puts",
                    params=[VariableDeclaration(name="string", vtype=Type(base="pointer", const=True, reference=Type(base="char")))],
                    body=Block([
                        VariableDeclaration(name="i", vtype=Type(base="int"), value=Int32(value=0)),
                        While(
                            condition=BinaryOperation(
                                operator="!=",
                                left=ArrayDereference(array=Variable(name="string"), index=Variable(name="i")),
                                right=Null()
                            ),
                            body=Block([
                                Call(name="putc", args=[ArrayDereference(array=Variable("string"), index=PostOperation(operator="++", variable=Variable(name="i")))])
                            ])
                        ),
                        Call(name="putc", args=[Char('\n')]),
                        ReturnStatement(
                            value=BinaryOperation(
                                operator="+",
                                left=Variable(name="i"),
                                right=Int32(value=1)
                            )
                        )
                    ])
                )
            ])
        )

    def test_main_function(self):
        self.assertEqual(
            parse("""
                int main(void) {
                    return puts("Hello, world!");
                }
            """),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="main",
                    params=[],
                    body=Block([
                        ReturnStatement(
                            value=Call(name="puts", args=[String("Hello, world!")])
                        )
                    ])
                )
            ])
        )

    def test_full_example(self):
        self.assertEqual(
            parse("""
                int main(void) {
                    return puts("Hello, world!");
                }

                int puts(const char * string) {
                    int i = 0;
                    while (string[i] != NULL) {
                        putc(string[i++]);
                    }
                    putc('\\n');
                    return i + 1;
                }
            """),
            Program([
                Function(
                    return_type=Type(base='int'),
                    name="puts",
                    params=[VariableDeclaration(name="string", vtype=Type(base="pointer", const=True, reference=Type(base="char")))],
                    body=Block([
                        VariableDeclaration(name="i", vtype=Type(base="int"), value=Int32(value=0)),
                        While(
                            condition=BinaryOperation(
                                operator="!=",
                                left=ArrayDereference(array=Variable(name="string"), index=Variable(name="i")),
                                right=Null()
                            ),
                            body=Block([
                                Call(name="putc", args=[ArrayDereference(array=Variable("string"), index=PostOperation(operator="++", variable=Variable(name="i")))])
                            ])
                        ),
                        Call(name="putc", args=[Char('\n')]),
                        ReturnStatement(
                            value=BinaryOperation(
                                operator="+",
                                left=Variable(name="i"),
                                right=Int32(value=1)
                            )
                        )

                    ])
                ),
                Function(
                    return_type=Type(base='int'),
                    name="main",
                    params=[],
                    body=Block([
                        ReturnStatement(
                            value=Call(name="puts", args=[String("Hello, world!")])
                        )
                    ])
                ),
            ])

        )
