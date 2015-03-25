from unittest import TestCase

from cycy.parser import ast


class TestNodes(TestCase):
    def test_repr(self):
        self.assertEqual(repr(ast.Int32(value=42)), "<Int32(value=42)>")
