from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase, skip
import sys

from bp.filepath import FilePath
from mock import patch

from cycy.interpreter import CyCy
from cycy.objects import W_Int32


class TestExample(TestCase):
    def setUp(self):
        self.cycy = CyCy()

    @skip("Integration test, will work eventually")
    def test_it_works(self):
        stdout = StringIO()
        with patch.object(sys, "stdout", stdout):
            self.cycy.interpret(
                FilePath(__file__).sibling("example.c").getContent(),
            )
        self.assertEqual(stdout.getvalue(), "Hello, world!\n")

    def test_it_does_fibonacci(self):
        source = dedent("""\
        int fib(int x) {
            while (x <= 2) {
                return 1;
            }
            return fib(x - 1) + fib(x - 2);
        }
        int main(void) {
            return fib(5);
        }
        """)

        main_return = self.cycy.interpret(source)
        self.assertEqual(W_Int32(5), main_return)
