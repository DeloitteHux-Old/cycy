from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase

from cycy.repl import REPL


class TestREPL(TestCase):
    def setUp(self):
        self.stdout, self.stderr = StringIO(), StringIO()
        self.repl = REPL(stdout=self.stdout, stderr=self.stderr)

    def test_it_handles_errors(self):
        self.repl.interpret("asdf\n")
        self.assertEqual(
            self.stdout.getvalue(), dedent(
                """\
                ParseError
                ----------

                asdf
                ^
                Unexpected IDENTIFIER 'asdf' at line 1, column 1
                """
            ),
        )
