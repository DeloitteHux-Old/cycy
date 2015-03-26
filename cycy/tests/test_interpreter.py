from unittest import TestCase
import os

from mock import patch

from cycy import interpreter
from cycy.objects import W_Char, W_Int32, W_Bool
from cycy.bytecode import *


class TestInterpreter(TestCase):
    def test_it_handles_opcodes_with_args(self):
        byte_code = Bytecode(
            instructions=[PUTC, 0],
            constants=[W_Char(ord("x"))],
            name="<some test bytecode>",
            number_of_variables=0,
        )

        with patch.object(os, "write") as os_write:
            interpreter.CyCy().run(byte_code)

            os_write.assert_called_once_with(
                1,  # file descriptor for stdout
                "x",
            )

    def test_it_handles_load_const(self):
        byte_code = Bytecode(
            instructions=[LOAD_CONST, 0],
            constants=[W_Int32(0)],
            name="<test_load_const>",
            number_of_variables=0,
        )

        stack = interpreter.CyCy().run(byte_code)

        self.assertEqual(stack, [W_Int32(0)])

    def test_binary_neq(self):
        byte_code_ne = Bytecode(
            instructions=[LOAD_CONST, 0, LOAD_CONST, 1, BINARY_NEQ, 0],
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_binary_neq>",
            number_of_variables=0,
        )
        byte_code_eq = Bytecode(
            instructions=[LOAD_CONST, 0, LOAD_CONST, 0, BINARY_NEQ, 0],
            constants=[W_Int32(0)],
            name="<test_binary_neq>",
            number_of_variables=0,
        )

        stack = interpreter.CyCy().run(byte_code_ne)
        self.assertEqual(stack, [W_Bool(True)])

        stack = interpreter.CyCy().run(byte_code_eq)
        self.assertEqual(stack, [W_Bool(False)])

    def test_binary_leq(self):
        byte_code_lt = Bytecode(
            instructions=[LOAD_CONST, 0, LOAD_CONST, 1, BINARY_LEQ, 0],
            constants=[W_Int32(1), W_Int32(0)],
            name="<test_binary_neq>",
            number_of_variables=0,
        )
        byte_code_leq = Bytecode(
            instructions=[LOAD_CONST, 0, LOAD_CONST, 0, BINARY_LEQ, 0],
            constants=[W_Int32(0)],
            name="<test_binary_neq>",
            number_of_variables=0,
        )
        byte_code_gt = Bytecode(
            instructions=[LOAD_CONST, 0, LOAD_CONST, 1, BINARY_LEQ, 0],
            constants=[W_Int32(0), W_Int32(1)],
            name="<test_binary_neq>",
            number_of_variables=0,
        )

        stack = interpreter.CyCy().run(byte_code_lt)
        self.assertEqual(stack, [W_Bool(True)])

        stack = interpreter.CyCy().run(byte_code_leq)
        self.assertEqual(stack, [W_Bool(True)])

        stack = interpreter.CyCy().run(byte_code_gt)
        self.assertEqual(stack, [W_Bool(False)])
