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

    @pg.production("return_statement : return expr ;")
    def return_statement(self, p):
        return ReturnStatement(value=p[1])

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
    @pg.production("statement_list : binop_expr ;")
    @pg.production("statement_list : declaration ;")
    @pg.production("statement_list : postincr ;")
    @pg.production("statement_list : assignment ;")
    @pg.production("statement_list : primary_expression ;")
    @pg.production("statement_list : func_call_statement")
    @pg.production("statement_list : dereference ;")
    def statement_list_return(self, p):
        return NodeList(items=[p[0]])

    @pg.production("func_call_statement : IDENTIFIER LEFT_BRACKET param_list RIGHT_BRACKET ;")
    def function_call_statement(self, p):
        return Call(name=p[0].getstr(), args=p[2].get_items())

    @pg.production("param_list : primary_expression")
    def param_list(self, p):
        return NodeList(items=[p[0]])

    @pg.production("assignment : IDENTIFIER = expr")
    def assign(self, p):
        return Assignment(left=Variable(p[0].getstr()), right=p[2])

    @pg.production('binop_expr : expr != expr')
    def binop_ne(self, p):
        return BinaryOperation(operator="!=", left=p[0], right=p[2])

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

    @pg.production("postincr : primary_expression ++")
    def post_incr(self, p):
        return PostOperation(operator="++", variable=p[0])

    @pg.production("expr : primary_expression")
    def expr_const(self, p):
        return p[0]

    @pg.production("primary_expression : const")
    @pg.production("primary_expression : IDENTIFIER")
    @pg.production("primary_expression : STRING")
    @pg.production("primary_expression : LEFT_BRACKET primary_expression RIGHT_BRACKET")
    def primary_expression(self, p):
        if isinstance(p[0], Node):
            # const
            return p[0]
        elif p[0].gettokentype() == "IDENTIFIER":
            return Variable(name=p[0].getstr())
        elif p[0].gettokentype() == "STRING":
            vals = []
            for v in p[0].getstr().strip('"'):
                vals.append(Char(value=v))
            vals.append(Char(value=chr(0)))
            return Array(value=vals)
        else:
            return p[1]

    @pg.production("const : INTEGER")
    @pg.production("const : CHAR")
    def const(self, p):
        if p[0].gettokentype() == "INTEGER":
            return Int32(int(p[0].getstr()))
        elif p[0].gettokentype() == "CHAR":
            return Char(p[0].getstr().strip("'"))
        raise AssertionError("Bad token type in const")

    parser = pg.build()

def parse(source):
    parser = SourceParser(lexer.lex(source))
    return parser.parse()
