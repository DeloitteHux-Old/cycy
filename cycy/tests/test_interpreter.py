from unittest import TestCase
import os

from mock import patch

from cycy import interpreter
from cycy.objects import W_Char
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
