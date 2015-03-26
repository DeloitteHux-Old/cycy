from unittest import TestCase

from cycy.parser.preprocessor import preprocess
import cycy.parser.preprocessor as preprocessor
from mock import patch

def clean(string):
    cleaned = []
    for line in string.split():
        line = line.strip()
        if line:
            cleaned.append(line)
    return "\n".join(cleaned)


class TestParser(TestCase):
    def test_include_statement(self):
        def fake_process_file(path, env):
            return "int foo(void) { bar; }"
        with patch.object(preprocessor, "preprocess_file", fake_process_file):
            pp = preprocess("""
                #include "foo.h"

                int main(void) { return 0; }
            """)

        self.assertEqual(clean(pp),
        clean("""
            int foo(void) { bar; }

            int main(void) { return 0; }
        """))
