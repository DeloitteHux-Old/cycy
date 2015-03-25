from rply import ParserGenerator
from .lexer import RULES, Lexer
from .ast import BinaryOperation, Int32


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

    @pg.production('binop : expr != expr')
    def binop_ne(self, p):
        return BinaryOperation(operand="!=", left=p[0], right=p[2])

    @pg.production("expr : INT")
    def expr_integer(self, p):
        return Int32(value=int(p[0].getstr()))


    # @pg.production('main : expr')
    # def main_expr(self, p):
    #     return p[0]
    #
    # @pg.production('expr : expr + expr')
    # def expr_plus(self, p):
    #     return BinaryOp("+", p[0], p[2])
    #
    # @pg.production('expr : T_NUMBER')
    # def expr_number(self, p):
    #     return ConstInt(int(p[0].getstr()))
    #
    # @pg.production('expr : T_FLOAT_NUMBER')
    # def expr_float_number(self, p):
    #     return ConstFloat(float(p[0].getstr()))
    #
    # @pg.production('expr : T_VARIABLE = expr')
    # def expr_variable_assign(self, p):
    #     return Assignment(p[0].getstr(), p[2])
    #
    # @pg.production('expr : expr ; expr')
    # def expr_semicolon(self, p):
    #     return SemicolonExpr(p[0], p[2])
    #
    # @pg.production('expr : T_VARIABLE')
    # def expr_variable(self, p):
    #     return Variable(p[0].getstr())

    parser = pg.build()

def parse(source):
    parser = SourceParser(Lexer().input(source, 0))
    return parser.parse()
