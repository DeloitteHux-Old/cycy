from StringIO import StringIO
from unittest import TestCase

from cycy.repl import REPL


class TestREPL(TestCase):
    def setUp(self):
        self.stdout, self.stderr = StringIO(), StringIO()
        self.repl = REPL(stdout=self.stdout, stderr=self.stderr)
