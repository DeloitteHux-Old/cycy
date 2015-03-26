from rply import ParserGenerator
from .lexer import lexer, RULES
from .ast import (
    Array,
    ArrayDereference,
    Assignment,
    BinaryOperation,
    Block,
    Call,
    Char,
    Function,
    Int32,
    Node,
    PostOperation,
    ReturnStatement,
    Variable,
    VariableDeclaration,
)

class NodeList(Node):
    """
    A list of nodes used for temporary accumulation during parsing, this
    should never appear in the final AST
    """
    def __init__(self, items=None):
        if items is None:
            items = []
        self.items = items

    def append(self, item):
        self.items.append(item)

    def get_items(self):
        return self.items

class SourceParser(object):
    """ Parse a given input using a lexer
    """

    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self):
        return self.parser.parse(self.lexer, state=self)

    pg = ParserGenerator(RULES,
                         cache_id='cycy',
    )

    @pg.production("main : function")
    def main_function(self, p):
        return p[0]

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

    @pg.production("main : return_statement")
    def main_return_statement(self, p):
        return p[0]

    @pg.production("main : func_call")
    def main_func_call(self, p):
        return p[0]

    @pg.production("return_statement : return expr ;")
    def main_return(self, p):
        return ReturnStatement(value=p[1])

    @pg.production("main : dereference")
    def expr_dereference(self, p):
        return p[0]

    @pg.production("function : INT32 IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET block")
    def function_void_param(self, p):
        return Function(
            return_type=p[0].gettokentype(),
            name=p[1].getstr(),
            params=[],
            body=p[5]
        )

    @pg.production("block : LEFT_CURLY_BRACKET statement_list RIGHT_CURLY_BRACKET")
    def block_statement_list(self, p):
        return Block(statements=p[1].get_items())

    @pg.production("statement_list : return_statement")
    def statement_list_return(self, p):
        return NodeList(items=[p[0]])

    @pg.production("func_call : IDENTIFIER LEFT_BRACKET param_list RIGHT_BRACKET ;")
    def function_call(self, p):
        return Call(name=p[0].getstr(), args=p[2].get_items())

    @pg.production("param_list : var")
    def param_list(self, p):
        return NodeList(items=[p[0]])

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

    @pg.production("expr : array LEFT_SQUARE_BRACKET expr RIGHT_SQUARE_BRACKET")
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
    parser = SourceParser(lexer.lex(source))
    return parser.parse()
