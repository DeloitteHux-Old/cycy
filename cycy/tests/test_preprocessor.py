from unittest import TestCase

from cycy.parser.core import Parser
from cycy.parser.preprocessor import Preprocessor


class FakeIncluder(object):
    def include(self, name):
        return ["stuff"]


class TestParser(TestCase):
    def setUp(self):
        self.preprocessor = Preprocessor(includers=[FakeIncluder()])
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
