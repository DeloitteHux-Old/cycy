from unittest import TestCase

from cycy.interpreter import CyCy
from cycy.objects import W_Int32
from cycy.parser.core import Parser
from cycy.parser.preprocessor import Included, Preprocessor


class FakeIncluder(object):
    def include(self, name, parser):
        return Included(
            tokens=parser.lexer.lex("int foo(void) {\nreturn 12;\n}\n"),
        )


class TestParser(TestCase):
    def setUp(self):
        self.preprocessor = Preprocessor(includers=[FakeIncluder()])
        self.parser = Parser(preprocessor=self.preprocessor)
        self.cycy = CyCy(parser=self.parser)

    def test_include_statement(self):
        w_return = self.cycy.interpret(
            [
                """
                #include "foo.h"

                int main(void) { return foo(); }
                """,
            ],
        )
        self.assertEqual(w_return, W_Int32(12))
