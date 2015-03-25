from StringIO import StringIO
from unittest import TestCase
import sys

from bp.filepath import FilePath
from mock import patch

from cycy.interpreter import interpret


class TestExample(TestCase):
    def test_it_works(self):
        stdout = StringIO()
        with patch.object(sys, "stdout", stdout):
            interpret(FilePath(".").sibling("example.c"))
        self.assertEqual(stdout.getvalue(), "Hello, world!\n")
