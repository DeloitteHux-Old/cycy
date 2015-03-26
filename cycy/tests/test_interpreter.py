from unittest import TestCase
import os

from mock import patch

from cycy import interpreter
from cycy.bytecode import *
from cycy.compiler import compile
from cycy.objects import W_Bool, W_Char, W_Function, W_Int32, W_String
from cycy.parser import parse


class TestInterpreterWithBytecode(TestCase):
    def test_it_handles_opcodes_with_args(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                PUTC, 0,
                RETURN, 0,
            ],
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
            instructions=[
                RETURN, 0,
            ],
            constants=[],
            name="<some test bytecode>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEquals(None, rv)

    def test_it_handles_load_const(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(0)],
            name="<test_load_const>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(0))

    def test_binary_neq(self):
        byte_code_ne = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 1,
                BINARY_NEQ, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_eq = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 0,
                BINARY_NEQ, 0,
                RETURN, 1,
            ],
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
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 1,
                BINARY_LEQ, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(1), W_Int32(0)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_leq = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 0,
                BINARY_LEQ, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(0)],
            name="<test_binary_neq>",
            arguments=(),
            variables={},
        )
        byte_code_gt = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 1,
                BINARY_LEQ, 0,
                RETURN, 1,
            ],
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
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 1,
                BINARY_ADD, NO_ARG,
                RETURN, 1
            ],
            constants=[W_Int32(1), W_Int32(2)],
            name="<test_binary_add>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(3))

    def test_binary_sub(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                LOAD_CONST, 1,
                BINARY_SUB, NO_ARG,
                RETURN, 1
            ],
            constants=[W_Int32(1), W_Int32(2)],
            name="<test_binary_add>",
            arguments=(),
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

    def test_store_and_load_variable(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                STORE_VARIABLE, 0,
                LOAD_VARIABLE, 0,
                RETURN, 1
            ],
            constants=[W_Int32(1)],
            name="<test_binary_add>",
            arguments=(),
            variables={"x": 0},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

    def test_it_calls_a_function_with_no_args(self):
        byte_code_caller = Bytecode(
            instructions=[
                CALL, 0,
                RETURN, 1,
            ],
            constants=[W_Function("callee", 0)],
            name="<test_calls_a_function_with_no_args>",
            arguments=(),
            variables={},
        )

        byte_code_callee = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(42)],
            name="<test_calls_a_function_with_no_args>",
            arguments=(),
            variables={},
        )

        interp = interpreter.CyCy()
        interp.compiled_functions = {
            "callee": byte_code_callee,
        }

        rv = interp.run(byte_code_caller)
        self.assertEqual(W_Int32(42), rv)

    def test_it_calls_a_function_with_one_arg(self):
        byte_code_caller = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                CALL, 1,
                RETURN, 1,
            ],
            constants=[W_Int32(42), W_Function("callee", 1)],
            name="<test_calls_a_function_with_no_args>",
            arguments=(),
            variables={},
        )

        byte_code_callee = Bytecode(
            instructions=[
                LOAD_VARIABLE, 0,
                RETURN, 1,
            ],
            constants=[],
            name="<test_calls_a_function_with_no_args>",
            arguments=["x"],
            variables={"x": 0},
        )

        interp = interpreter.CyCy()
        interp.compiled_functions = {
            "callee": byte_code_callee,
        }

        rv = interp.run(byte_code_caller)
        self.assertEqual(W_Int32(42), rv)

    def test_array_dereferences(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                STORE_VARIABLE, 0,
                LOAD_CONST, 1,
                LOAD_VARIABLE, 0,
                DEREFERENCE, NO_ARG,
                RETURN, 1,
            ],
            constants=[W_String("bar"), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={"foo": ""},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Char("a"))

    def test_jump(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 0,
                JUMP, 6,   # jump to just past LOAD_CONST 1
                LOAD_CONST, 1,
                RETURN, 1,
            ],
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(0))

    def test_jump_if_not_zero(self):
        byte_code = Bytecode(
            instructions=[
                LOAD_CONST, 1,
                LOAD_CONST, 1,
                JUMP_IF_NOT_ZERO, 8,   # jump to just past LOAD_CONST 0
                LOAD_CONST, 0,
                RETURN, 1,
            ],
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_array_dereferences>",
            arguments=[],
            variables={},
        )

        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(1))

class TestInterperterWithC(TestCase):

    def get_bytecode(self, source, func_name="main"):
        program = parse(source)
        return compile(next(f for f in program.functions() if f.name == func_name))

    def test_binary_leq(self):
        byte_code_lt = self.get_bytecode("int main(void) { return 1 <= 2; }")
        rv = interpreter.CyCy().run(byte_code_lt)
        self.assertEqual(rv, W_Bool(True))

        byte_code_leq = self.get_bytecode("int main(void) { return 1 <= 1; }")
        rv = interpreter.CyCy().run(byte_code_leq)
        self.assertEqual(rv, W_Bool(True))

        byte_code_gt = self.get_bytecode("int main(void) { return 2 <= 1; }")
        rv = interpreter.CyCy().run(byte_code_gt)
        self.assertEqual(rv, W_Bool(False))

    def test_binary_sub(self):
        byte_code = self.get_bytecode("int main(void) { return 7 - 3; }")
        rv = interpreter.CyCy().run(byte_code)
        self.assertEqual(rv, W_Int32(4))
