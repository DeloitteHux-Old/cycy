from rply import ParserGenerator
from .preprocessor import preprocess
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
    Null,
    PostOperation,
    Program,
    ReturnStatement,
    Variable,
    VariableDeclaration,
    While,
    Type,
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

    def extend(self, items):
        self.items.extend(items)

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

    @pg.production("main : program")
    def main_program(self, p):
        return p[0]

    @pg.production("program : function")
    def program_function(self, p):
        return Program([p[0]])

    @pg.production("program : function program")
    def program_function_program(self, p):
        p[1].add_function(p[0])
        return p[1]

    @pg.production("return_statement : return expr ;")
    @pg.production("return_statement : return func_call_statement")
    def return_statement(self, p):
        return ReturnStatement(value=p[1])

    @pg.production("function : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET block")
    def function_void_param(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[],
            body=p[5]
        )

    @pg.production("function : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET block")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=p[3].get_items(),
            body=p[5]
        )

    @pg.production("arg_decl_list : declaration")
    def arg_decl_list_arg_decl(self, p):
        return NodeList([p[0]])

    @pg.production("block : LEFT_CURLY_BRACKET statement_list RIGHT_CURLY_BRACKET")
    def block_statement_list(self, p):
        return Block(statements=p[1].get_items())

    @pg.production("statement_list : statement")
    def statement_list_statement(self, p):
        return NodeList([p[0]])

    @pg.production("statement_list : statement statement_list")
    def statement_list_statement_list(self, p):
        st = NodeList([p[0]])
        st.extend(p[1].get_items())
        return st

    @pg.production("statement : return_statement")
    @pg.production("statement : expr ;")
    @pg.production("statement : declaration ;")
    @pg.production("statement : assignment ;")
    @pg.production("statement : primary_expression ;")
    @pg.production("statement : func_call_statement")
    @pg.production("statement : while_loop")
    def statement_list_return(self, p):
        return p[0]

    @pg.production("while_loop : while LEFT_BRACKET expr RIGHT_BRACKET block")
    def while_loop(self, p):
        return While(condition=p[2], body=p[4])

    @pg.production("func_call : IDENTIFIER LEFT_BRACKET param_list RIGHT_BRACKET")
    def function_call(self, p):
        return Call(name=p[0].getstr(), args=p[2].get_items())

    @pg.production("func_call_statement : func_call ;")
    @pg.production("expr : func_call")
    def function_call_expr(self, p):
        return p[0]

    @pg.production("param_list : expr")
    def param_list(self, p):
        return NodeList(items=[p[0]])

    @pg.production("assignment : IDENTIFIER = expr")
    def assign(self, p):
        return Assignment(left=Variable(p[0].getstr()), right=p[2])

    @pg.production('expr : expr != expr')
    def binop_ne(self, p):
        return BinaryOperation(operator="!=", left=p[0], right=p[2])

    @pg.production("expr : expr + expr")
    def binop_add(self, p):
        return BinaryOperation(operator="+", left=p[0], right=p[2])

    @pg.production("expr : expr - expr")
    def binop_sub(self, p):
        return BinaryOperation(operator="-", left=p[0], right=p[2])

    @pg.production("expr : expr <= expr")
    def binop_le(self, p):
        return BinaryOperation(operator="<=", left=p[0], right=p[2])

    @pg.production("expr : STRING")
    def expr_string(self, p):
        vals = []
        for v in p[0].getstr().strip('"'):
            vals.append(Char(value=v))
        vals.append(Char(value=chr(0)))
        return Array(value=vals)

    @pg.production("expr : null")
    def expr_null(self, p):
        return Null()

    @pg.production("expr : array LEFT_SQUARE_BRACKET expr RIGHT_SQUARE_BRACKET")
    def array_dereference(self, p):
        return ArrayDereference(array=p[0], index=p[2])

    @pg.production("array : IDENTIFIER")
    def array_variable(self, p):
        return Variable(name=p[0].getstr())

    @pg.production("declaration : type IDENTIFIER")
    def declare_int(self, p):
        return VariableDeclaration(name=p[1].getstr(), vtype=p[0], value=None)

    @pg.production("declaration : type IDENTIFIER = INTEGER")
    def declare_assign_int(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=Int32(int(p[3].getstr()))
        )

    @pg.production("type : optional_const core_or_pointer_type")
    def type_object(self, p):
        p[1].const = p[0]
        return p[1]

    @pg.production("optional_const : ")
    def const_false(self, p):
        return False

    @pg.production("optional_const : CONST")
    def const_true(self, p):
        return True

    @pg.production("core_or_pointer_type : core_type")
    def core_type(self, p):
        return p[0]

    @pg.production("core_or_pointer_type : core_or_pointer_type *")
    def pointer_type(self, p):
        return Type(base="pointer", reference=p[0])

    @pg.production("core_type : INT")
    @pg.production("core_type : CHAR")
    def vtype(self, p):
        return Type(base=p[0].getstr())

    @pg.production("arg_decl : INT IDENTIFIER")
    def int32_param(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype="INT"
        )

    @pg.production("expr : primary_expression ++")
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

    @pg.error
    def error_handler(self, token):
        raise ValueError(
            "Unexpected %s at line %s col %s" % (
                token.gettokentype(),
                token.source_pos.lineno,
                token.source_pos.colno,
            )
        )

    parser = pg.build()

def parse(source):
    lexed = lexer.lex(preprocess(source))
    parser = SourceParser(lexed)
    return parser.parse()
