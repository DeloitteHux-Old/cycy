from StringIO import StringIO
from textwrap import dedent
from unittest import TestCase, skip

from bp.filepath import FilePath

from cycy.interpreter import CyCy
from cycy.objects import W_Int32


class TestExample(TestCase):
    def setUp(self):
        self.stdout, self.stderr = StringIO(), StringIO()
        self.cycy = CyCy(stdout=self.stdout, stderr=self.stderr)

    @skip("Integration test, will work eventually")
    def test_it_works(self):
        self.cycy.interpret(
            [FilePath(__file__).sibling("example.c").getContent()],
        )
        self.assertEqual(self.stdout.getvalue(), "Hello, world!\n")

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

        w_returned = self.cycy.interpret([source])
        self.assertEqual(w_returned, W_Int32(5))
