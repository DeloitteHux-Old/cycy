from unittest import TestCase

from cycy.parser import parse
from cycy.parser.ast import BinaryOperation, Int32

class TestParser(TestCase):
    def test_basic_ne(self):
        self.assertEqual(
            parse('2 != 3'),
            BinaryOperation("!=", Int32(2), Int32(3))
        )
