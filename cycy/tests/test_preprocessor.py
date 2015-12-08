from unittest import TestCase

from cycy.environment import Environment
from cycy.interpreter import CyCy
from cycy.parser.preprocessor import Preprocessor
from cycy.parser.sourceparser import Parser


class FakeIncluder(object):
    def include(self, name):
        return ["stuff"]


class TestParser(TestCase):
    def setUp(self):
        self.environment = Environment(includers=[FakeIncluder()])
        self.preprocessor = Preprocessor(environment=self.environment)
        self.parser = Parser(preprocessor=self.preprocessor)

    def preprocess(self, source):
        return list(
            self.preprocessor.preprocessed(tokens=self.parser.parse(source))
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
