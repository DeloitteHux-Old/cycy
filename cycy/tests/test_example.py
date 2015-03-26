from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase, skip
import sys

from bp.filepath import FilePath
from mock import patch

from cycy.interpreter import interpret_source


class TestExample(TestCase):
    @skip("Integration test, will work eventually")
    def test_it_works(self):
        stdout = StringIO()
        with patch.object(sys, "stdout", stdout):
            interpret(FilePath(__file__).sibling("example.c").getContent())
        self.assertEqual(stdout.getvalue(), "Hello, world!\n")

    @skip("Integration test, will work eventually")
    def test_it_does_fibonacci(self):
        source = dedent("""\
        int fib(int x) {
            int x;
            while (x <= 2) {
                return 1;
            }
            return fib(x - 1) + fib(x - 2);
        }
        int main(void) {
            return fib(5);
        }
        """)

        main_return = interpret_source(source)
        self.assertEqual(5, main_return)
