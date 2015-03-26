from unittest import TestCase
import os

from mock import patch

from cycy import interpreter
from cycy.objects import W_Char, W_Int32, W_Bool, w_null
from cycy.bytecode import *


class TestInterpreter(TestCase):
    def test_it_handles_opcodes_with_args(self):
        byte_code = Bytecode(
            instructions=[
                PUTC, 0,
                RETURN, 0,
            ],
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

    def test_it_can_return_no_value(self):
        # this is not the same as a C function returning NULL,
        # it is a void C function that has no return value
        byte_code = Bytecode(
            instructions=[
                RETURN, 0,
            ],
            constants=[],
            name="<some test bytecode>",
            number_of_variables=0,
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
            number_of_variables=0,
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
            number_of_variables=0,
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
            number_of_variables=0,
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
            number_of_variables=0,
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
            number_of_variables=0,
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
            number_of_variables=0,
        )

        rv = interpreter.CyCy().run(byte_code_lt)
        self.assertEqual(rv, W_Bool(True))

        rv = interpreter.CyCy().run(byte_code_leq)
        self.assertEqual(rv, W_Bool(True))

        rv = interpreter.CyCy().run(byte_code_gt)
        self.assertEqual(rv, W_Bool(False))
