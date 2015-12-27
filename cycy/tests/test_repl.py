from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase

from cycy.interpreter import CyCy
from cycy.parser.core import IncrementalParser
from cycy.repl import REPL


class TestREPL(TestCase):
    def setUp(self):
        self.repl = REPL(
            interpreter=CyCy(
                parser=IncrementalParser(),
                stdin=StringIO(),
                stdout=StringIO(),
                stderr=StringIO(),
            )
        )

    def test_it_handles_errors(self):
        self.repl.interpret("asdf\n")
        self.assertEqual(
            self.repl.stdout.getvalue(), dedent(
                """\
                ParseError
                ----------

                asdf
                ^
                Unexpected IDENTIFIER 'asdf' at line 1, column 1
                """
            ),
        )

    def test_it_buffers_incremental_input(self):
        self.repl.interpret("int main(void) {\n")
        self.repl.interpret("return 2;\n")
        self.repl.interpret("}\n")
        self.assertEqual(self.repl.stdout.getvalue(), "2")

        # and then gets rid of the buffer
        self.repl.interpret("int main(void) { return 3; }\n")
        self.assertEqual(self.repl.stdout.getvalue(), "23")
