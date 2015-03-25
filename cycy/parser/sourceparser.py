from rply import ParserGenerator
from .lexer import RULES, Lexer
from .ast import (
    Array,
    BinaryOperation,
    Char,
    Int32,
    VariableDeclaration,
    PostOperation,
    Variable,
    Assignment,
    ArrayDereference
)

class SourceParser(object):
    """ Parse a given input using a lexer
    """

    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self):
        return self.parser.parse(self.lexer, state=self)

    pg = ParserGenerator([d for _, d in RULES],
                         cache_id='cycy',
    )

    @pg.production('main : binop')
    def main_binop(self, p):
        return p[0]

    @pg.production('main : declaration')
    def main_declaration(self, p):
        return p[0]

    @pg.production("main : postincr")
    def main_postincr(self, p):
        return p[0]

    @pg.production("main : assign")
    def main_assign(self, p):
        return p[0]

    @pg.production("main : expr")
    def main_expr(self, p):
        return p[0]

    @pg.production("main : dereference")
    def expr_dereference(self, p):
        return p[0]

    @pg.production("assign : var = expr")
    def assign(self, p):
        return Assignment(left=p[0], right=p[2])

    @pg.production('binop : expr != expr')
    def binop_ne(self, p):
        return BinaryOperation(operator="!=", left=p[0], right=p[2])

    @pg.production("expr : INTEGER")
    def expr_integer(self, p):
        return Int32(value=int(p[0].getstr()))

    @pg.production("expr : CHAR")
    def expr_char(self, p):
        return Char(value=p[0].getstr().strip("'"))

    @pg.production("expr : STRING")
    def expr_string(self, p):
        vals = []
        for v in p[0].getstr().strip('"'):
            vals.append(Char(value=v))
        vals.append(Char(value=chr(0)))
        return Array(value=vals)

    @pg.production("dereference : array LEFT_SQUARE_BRACKET expr RIGHT_SQUARE_BRACKET")
    def array_dereference(self, p):
        return ArrayDereference(array=p[0], index=p[2])

    @pg.production("array : IDENTIFIER")
    def array_variable(self, p):
        return Variable(name=p[0].getstr())

    @pg.production("declaration : INT32 IDENTIFIER")
    def declare_int(self, p):
        return VariableDeclaration(name=p[1].getstr(), vtype="INT32", value=None)

    @pg.production("postincr : var ++")
    def post_incr(self, p):
        return PostOperation(operator="++", variable=p[0])

    @pg.production("var : IDENTIFIER")
    def var_variable(self, p):
        return Variable(name=p[0].getstr())

    parser = pg.build()

def parse(source):
    parser = SourceParser(Lexer().input(source, 0))
    return parser.parse()
    print("")
