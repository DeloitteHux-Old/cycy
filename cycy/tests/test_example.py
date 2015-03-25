from StringIO import StringIO
from unittest import TestCase, skip
import sys

from bp.filepath import FilePath
from mock import patch

from cycy.interpreter import interpret


class TestExample(TestCase):
    @skip("Integration test, will work eventually")
    def test_it_works(self):
        stdout = StringIO()
        with patch.object(sys, "stdout", stdout):
            interpret(FilePath(__file__).sibling("example.c").getContent())
        self.assertEqual(stdout.getvalue(), "Hello, world!\n")
