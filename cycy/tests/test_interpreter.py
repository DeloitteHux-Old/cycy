from StringIO import StringIO
from unittest import TestCase
import sys

from mock import patch

from cycy import interpreter
from cycy.bytecode import *


class TestInterpreter(TestCase):
    def test_it_handles_opcodes_with_args(self):
        constants = [ord("x")]
        instructions = [PUTC, 0]
        byte_code = Bytecode(
            instructions=instructions,
            constants=constants,
            name="<still don't know>",
            number_of_variables=0,
        )

        stdout = StringIO()
        with patch.object(sys, "stdout", stdout):
            interpreter.CyCy().run(byte_code)

        self.assertEqual(
            stdout.getvalue(),
            "x",
        )
