
from rpython.rlib.rsre.rsre_re import compile, M, DOTALL
from rply.token import Token, SourcePosition

RULES = [
    ("\d+", "INTEGER"),
    ("'.'", "CHAR"),
    ("\".*\"", "STRING"),
    ("int", "INT32"),
    ("[_a-zA-Z][_a-zA-Z0-9]*", "IDENTIFIER"),
    ("\[", "LEFT_SQUARE_BRACKET"),
    ("\]", "RIGHT_SQUARE_BRACKET"),
    ("=", "="),
    ("!=", "!="),
    ("\+\+", "++")
]

class LexerError(Exception):
    pass

class TokenRule:
    def __init__(self, rule, token_type):
        self.rule = rule
        self.token_type = token_type

class Lexer(object):
    """ Lexer object creates a list of tokens for a given input.
    Use:

    lexer.input(buf, startpos, lineno) and use it as an iterator
    """
    def __init__(self):
        self.rules = []
        for regex, type in RULES:
            self.rules.append(TokenRule(compile(regex, M | DOTALL), type))

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
        for trule in self.rules:
            m = trule.rule.match(self.buf, pos=pos)
            if m:
                self.pos = m.end()
                while self.pos < len(self.buf) and self.buf[self.pos] == " ":
                    self.pos += 1
                return Token(trule.token_type, self.buf[m.start():m.end()],
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
