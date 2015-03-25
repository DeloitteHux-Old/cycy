
from rpython.rlib.rsre.rsre_re import compile, M, DOTALL
from rply.token import Token, SourcePosition

RULES = [
    ("\d+", "INT"),
    ("!=", "!=")
]

class LexerError(Exception):
    pass

class Lexer(object):
    """ Lexer object creates a list of tokens for a given input.
    Use:

    lexer.input(buf, startpos, lineno) and use it as an iterator
    """
    def __init__(self):
        self.rules = []
        for regex, type in RULES:
            self.rules.append((compile(regex, M | DOTALL), type))

    def input(self, buf, pos):
        """ Initialize the lexer with a buffer as input.
        """
        self.buf = buf
        self.pos = pos
        return self

    def __iter__(self):
        return self

    def token(self):
        pos = self.pos
        for token_regex, token_type in self.rules:
            m = token_regex.match(self.buf, pos=pos)
            if m:
                self.pos = m.end()
                return Token(token_type, self.buf[m.start():m.end()],
                             SourcePosition(pos, 0, pos))
        raise LexerError("Unrecognized token starting at %s" %
                         self.buf[self.pos:self.pos+10])

    def next(self):
        if self.pos >= len(self.buf):
            return None
        t = self.token()
        return t

def lexer_run(source):
    l = Lexer()
    res = []
    for item in l.input(source, 0):
        if item is not None:
            res.append(item)
        else:
            break
    return res
