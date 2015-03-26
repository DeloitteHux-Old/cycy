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
    Double,
    Node,
    Null,
    PostOperation,
    PreOperation,
    Program,
    ReturnStatement,
    String,
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

class BoolWrapper(Node):
    pass

BoolTrue = BoolWrapper()
BoolFalse = BoolWrapper()

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

    @pg.production("program : unit")
    def program_function(self, p):
        return Program([p[0]])

    @pg.production("program : unit program")
    def program_unit_program(self, p):
        p[1].add_unit(p[0])
        return p[1]

    @pg.production("return_statement : return expr ;")
    @pg.production("return_statement : return func_call_statement")
    def return_statement(self, p):
        return ReturnStatement(value=p[1])

    @pg.production("unit : function")
    @pg.production("unit : prototype")
    def unit(self, p):
        return p[0]

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

    @pg.production("prototype : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET ;")
    def function_void_param(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[],
            prototype=True
        )

    @pg.production("prototype : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET ;")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=p[3].get_items(),
            prototype=True
        )

    @pg.production("prototype : type IDENTIFIER LEFT_BRACKET type_list RIGHT_BRACKET ;")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[VariableDeclaration(name=None, vtype=x, value=None) for x in p[3].get_items()],
            prototype=True
        )

    @pg.production("arg_decl_list : declaration")
    def arg_decl_list_declaration(self, p):
        return NodeList([p[0]])

    @pg.production("arg_decl_list : arg_decl_list , declaration")
    def arg_decl_list(self, p):
        p[0].append(p[2])
        return p[0]

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

    @pg.production("expr : expr - expr")
    @pg.production("expr : expr + expr")
    @pg.production("expr : expr * expr")
    @pg.production("expr : expr / expr")
    @pg.production("expr : expr % expr")
    @pg.production('expr : expr || expr')
    @pg.production('expr : expr && expr')
    @pg.production('expr : expr == expr')
    @pg.production('expr : expr != expr')
    @pg.production("expr : expr <= expr")
    @pg.production("expr : expr >= expr")
    @pg.production("expr : expr < expr")
    @pg.production("expr : expr > expr")
    def binop(self, p):
        return BinaryOperation(operator=p[1].getstr(), left=p[0], right=p[2])

    @pg.production("expr : STRING_LITERAL")
    def expr_string(self, p):
        return String(p[0].getstr().strip("\""))

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

    @pg.production("declaration : type IDENTIFIER = INTEGER_LITERAL")
    def declare_assign_int(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=Int32(int(p[3].getstr()))
        )

    @pg.production("declaration : type IDENTIFIER = FLOAT_LITERAL")
    def declare_assign_float(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=Double(float(p[3].getstr()))
        )

    @pg.production("declaration : type IDENTIFIER = STRING_LITERAL")
    def declare_assign_string(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=String(p[3].getstr().strip("\""))
        )

    @pg.production("type_list : type")
    def type_list(self, p):
        return NodeList([p[0]])

    @pg.production("type_list : type_list , type")
    def type_list_type(self, p):
        p[0].append(p[2])
        return p[0]

    @pg.production("type : optional_unsigned optional_const core_or_pointer_type")
    def type_object(self, p):
        the_type = p[2]
        assert isinstance(the_type, Type)
        the_type.unsigned = (p[0] == BoolTrue)
        the_type.const = (p[1] == BoolTrue)
        return the_type

    @pg.production("optional_const : ")
    def const_false(self, p):
        return BoolFalse

    @pg.production("optional_const : CONST")
    def const_true(self, p):
        return BoolTrue

    @pg.production("optional_unsigned : ")
    def unsigned_false(self, p):
        return BoolFalse

    @pg.production("optional_unsigned : UNSIGNED")
    def unsigned_true(self, p):
        return BoolTrue

    @pg.production("core_or_pointer_type : core_type")
    def core_type(self, p):
        return p[0]

    @pg.production("core_or_pointer_type : core_or_pointer_type *")
    def pointer_type(self, p):
        return Type(base="pointer", reference=p[0])

    @pg.production("core_type : CHAR")
    @pg.production("core_type : INT")
    @pg.production("core_type : SHORT")
    @pg.production("core_type : LONG")
    @pg.production("core_type : FLOAT")
    @pg.production("core_type : DOUBLE")
    def generic_vtype(self, p):
        return Type(base=p[0].getstr())

    @pg.production("core_type : LONG LONG")
    def long_long_vtype(self, p):
        return Type(base='long long')

    @pg.production("core_type : LONG DOUBLE")
    def long_double_vtype(self, p):
        return Type(base='long double')

    @pg.production("expr : primary_expression ++")
    def post_incr(self, p):
        return PostOperation(operator="++", variable=p[0])

    @pg.production("expr : primary_expression --")
    def post_incr(self, p):
        return PostOperation(operator="--", variable=p[0])

    @pg.production("expr : ++ primary_expression")
    def post_incr(self, p):
        return PreOperation(operator="++", variable=p[1])

    @pg.production("expr : -- primary_expression")
    def post_incr(self, p):
        return PreOperation(operator="--", variable=p[1])

    @pg.production("expr : primary_expression")
    def expr_const(self, p):
        return p[0]

    @pg.production("primary_expression : const")
    @pg.production("primary_expression : IDENTIFIER")
    @pg.production("primary_expression : STRING_LITERAL")
    @pg.production("primary_expression : LEFT_BRACKET primary_expression RIGHT_BRACKET")
    def primary_expression(self, p):
        if isinstance(p[0], Node):
            # const
            return p[0]
        elif p[0].gettokentype() == "IDENTIFIER":
            return Variable(name=p[0].getstr())
        elif p[0].gettokentype() == "STRING_LITERAL":
            vals = []
            for v in p[0].getstr().strip('"'):
                vals.append(Char(value=v))
            vals.append(Char(value=chr(0)))
            return Array(value=vals)
        else:
            return p[1]

    @pg.production("const : FLOAT_LITERAL")
    @pg.production("const : INTEGER_LITERAL")
    @pg.production("const : CHAR_LITERAL")
    def const(self, p):
        if p[0].gettokentype() == "INTEGER_LITERAL":
            return Int32(int(p[0].getstr()))
        elif p[0].gettokentype() == "FLOAT_LITERAL":
            return Double(float(p[0].getstr()))
        elif p[0].gettokentype() == "CHAR_LITERAL":
            return Char(p[0].getstr().strip("'"))
        raise AssertionError("Bad token type in const")

    @pg.error
    def error_handler(self, token):
        source_pos = token.source_pos
        if source_pos is None:
            raise ValueError("Unexpected %s" % (token.gettokentype()))
        raise ValueError(
            "Unexpected %s at line %s col %s" % (
                token.gettokentype(),
                source_pos.lineno,
                source_pos.colno,
            )
        )

    parser = pg.build()

def parse(source, environment=None):
    lexed = lexer.lex(preprocess(source, environment))
    parser = SourceParser(lexed)
    return parser.parse()
