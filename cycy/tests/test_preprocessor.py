from unittest import TestCase

from cycy.environment import Environment
from cycy.interpreter import CyCy
from cycy.parser.lexer import lexer
from cycy.parser.preprocessor import preprocessed


class FakeIncluder(object):
    def include(self, name):
        return ["stuff"]


class TestParser(TestCase):
    def setUp(self):
        self.environment = Environment(includers=[FakeIncluder()])
        self.cycy = CyCy(environment=self.environment)

    def preprocess(self, source):
        return list(
            preprocessed(
                tokens=lexer.lex(source),
                interpreter=self.cycy,
            )
        )
    def test_include_statement(self):
        self.skipTest("Skipped until this is easier.")
        tokens = self.preprocess(
            """
            #include "foo.h"

            int main(void) { return 0; }
            """,
        )
        self.assertEqual(
            tokens,
            [],
        )
