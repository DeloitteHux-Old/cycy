from unittest import TestCase
import os

from mock import patch
from rply.token import Token

from cycy import compiler, interpreter
from cycy.bytecode import (
    BINARY_ADD,
    BINARY_LEQ,
    BINARY_NEQ,
    BINARY_SUB,
    CALL,
    DEREFERENCE,
    JUMP,
    JUMP_IF_NOT_ZERO,
    JUMP_IF_ZERO,
    LOAD_CONST,
    LOAD_VARIABLE,
    NO_ARG,
    PUTC,
    RETURN,
    STORE_VARIABLE,
    Bytecode,
)
from cycy.objects import W_Bool, W_Char, W_Function, W_Int32, W_String
from cycy.parser.core import ParseError


class TestInterpreter(TestCase):
    pass


class TestInterpreterWithBytecode(TestCase):
    def test_it_handles_opcodes_with_args(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    PUTC, 0,
                    RETURN, 0,
                ]
            ),
            constants=[W_Char("x")],
            name="<some test bytecode>",
            arguments=(),
            variables={},
        )

        with patch.object(os, "write") as os_write:
            interpreter.CyCy().run(byte_code)

            os_write.assert_called_once_with(
                1,  # file descriptor for stdout
                "x",
            )

    def test_it_can_return_no_value(self):
        # this is not the same as a C function returning NULL,
        # it is a void C function that has no return value
        byte_code = Bytecode(
            tape=compiler.Tape(instructions=[RETURN, 0]),
            constants=[],
            name="<some test bytecode>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEquals(None, rv)

    def test_it_handles_load_const(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0)],
            name="<test_load_const>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(0))

    def test_binary_neq(self):
        byte_code_ne = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 1,
                    BINARY_NEQ, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_eq = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 0,
                    BINARY_NEQ, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code_ne)
        self.assertEqual(rv, W_Bool(True))

        rv = interpreter.CyCy().run(byte_code_eq)
        self.assertEqual(rv, W_Bool(False))

    def test_binary_leq(self):
        byte_code_lt = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 1,
                    BINARY_LEQ, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(1), W_Int32(0)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_leq = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 0,
                    BINARY_LEQ, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_gt = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 1,
                    BINARY_LEQ, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code_lt)
        self.assertEqual(rv, W_Bool(True))

        rv = interpreter.CyCy().run(byte_code_leq)
        self.assertEqual(rv, W_Bool(True))

        rv = interpreter.CyCy().run(byte_code_gt)
        self.assertEqual(rv, W_Bool(False))

    def test_binary_add(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 1,
                    BINARY_ADD, NO_ARG,
                    RETURN, 1
                ]
            ),
            constants=[W_Int32(1), W_Int32(2)],
            name="<test_binary_add>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(3))

    def test_binary_sub(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 1,
                    BINARY_SUB, NO_ARG,
                    RETURN, 1
                ]
            ),
            constants=[W_Int32(1), W_Int32(2)],
            name="<test_binary_add>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

    def test_store_and_load_variable(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    STORE_VARIABLE, 0,
                    LOAD_VARIABLE, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(1)],
            name="<test_binary_add>",
            arguments=(),
            variables={"x": 0},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

    def test_it_calls_a_function_with_no_args(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    CALL, 0,
                    RETURN, 1,
                ]
            ),
            constants=[
                W_Function(
                    name="callee",
                    arity=0,
                    bytecode=Bytecode(
                        name="<the callee's bytecode>",
                        arguments=(),
                        variables={},
                        constants=[W_Int32(42)],
                        tape=compiler.Tape(
                            instructions=[
                                LOAD_CONST, 0,
                                RETURN, 1,
                            ]
                        ),
                    ),
                )
            ],
            name="<test_calls_a_function_with_no_args>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(42))

    def test_it_calls_a_function_with_one_arg(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    CALL, 1,
                    RETURN, 1,
                ],
            ),
            constants=[
                W_Int32(42), W_Function(
                    name="callee",
                    arity=1,
                    bytecode=Bytecode(
                        name="<the callee's bytecode>",
                        arguments=["x"],
                        variables={"x": 0},
                        constants=[W_Int32(42)],
                        tape=compiler.Tape(
                            instructions=[
                                LOAD_VARIABLE, 0,
                                RETURN, 1,
                            ]
                        ),
                    ),
                ),
            ],
            name="<test_calls_a_function_with_no_args>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(42))

    def test_array_dereferences(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    STORE_VARIABLE, 0,
                    LOAD_CONST, 1,
                    LOAD_VARIABLE, 0,
                    DEREFERENCE, NO_ARG,
                    RETURN, 1,
                ]
            ),
            constants=[W_String("bar"), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={"foo": ""},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Char("a"))

    def test_jump(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    JUMP, 6,   # jump to just past LOAD_CONST 1
                    LOAD_CONST, 1,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(0))

    def test_jump_if_not_zero(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 1,
                    LOAD_CONST, 1,
                    JUMP_IF_NOT_ZERO, 8,   # jump to just past LOAD_CONST 0
                    LOAD_CONST, 0,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

    def test_jump_if_zero(self):
        byte_code = Bytecode(
            tape=compiler.Tape(
                instructions=[
                    LOAD_CONST, 0,
                    LOAD_CONST, 0,
                    JUMP_IF_ZERO, 8,   # jump to just past LOAD_CONST 0
                    LOAD_CONST, 1,
                    RETURN, 1,
                ]
            ),
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(0))


class TestInterpreterWithC(TestCase):
    """
    Test interpretation of C bytecode in integration with the parser.

    """

    def setUp(self):
        self.interpreter = interpreter.CyCy()
        self.parser = self.interpreter.parser
        self.compiler = self.interpreter.compiler

    def get_bytecode(self, source, func_name="main"):
        self.compiler.compile(self.parser.parse(source))
        w_func = self.compiler.constants[self.compiler.functions[func_name]]
        return w_func.bytecode

    def test_binary_leq(self):
        byte_code_lt = self.get_bytecode("int main(void) { return 1 <= 2; }")
        rv = self.interpreter.run(byte_code_lt)
        self.assertEqual(rv, W_Bool(True))

        byte_code_leq = self.get_bytecode("int main(void) { return 1 <= 1; }")
        rv = self.interpreter.run(byte_code_leq)
        self.assertEqual(rv, W_Bool(True))

        byte_code_gt = self.get_bytecode("int main(void) { return 2 <= 1; }")
        rv = self.interpreter.run(byte_code_gt)
        self.assertEqual(rv, W_Bool(False))

    def test_binary_sub(self):
        byte_code = self.get_bytecode("int main(void) { return 7 - 3; }")
        rv = self.interpreter.run(byte_code)
        self.assertEqual(rv, W_Int32(4))

    def test_while_loop(self):
        byte_code = self.get_bytecode(
            "int main(void) {"
            "  int x = 0;"
            "  int i = 3;"
            "  while (i) {"
            "    x = x + 1;"
            "    i = i - 1;"
            "  }"
            "  return x;"
            "}"
        )

        rv = self.interpreter.run(byte_code)
        self.assertEqual(rv, W_Int32(3))


class TestInterpreterIntegration(TestCase):
    def test_unknown_function_call(self):
        errors = []
        cycy = interpreter.CyCy(handle_error=errors.append)
        cycy.interpret(["int main(void) { return canhazprint(0); }"])
        self.assertEqual(errors, [compiler.NoSuchFunction("canhazprint")])

    def test_parse_error(self):
        errors = []
        cycy = interpreter.CyCy(handle_error=errors.append)
        cycy.interpret(["asdf"])
        self.assertEqual(
            errors, [
                ParseError(token=Token("IDENTIFIER", "asdf"), source="asdf"),
            ],
        )
