from rply import ParserGenerator

from cycy.exceptions import CyCyError
from cycy.parser.ast import (
    Array,
    ArrayDereference,
    Assembler,
    Assignment,
    BinaryOperation,
    Block,
    Call,
    Char,
    For,
    Function,
    If,
    Include,
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
    Type,
)
from cycy.parser.lexer import RULES


class LexingError(CyCyError):
    def __init__(self, source_pos, message):
        self.message = message
        self.source_pos = source_pos

    def __str__(self):
        return "Lexer failed at %s (message: %s)" % (
            self.source_pos, self.message,
        )


class ParseError(CyCyError):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        token_type = self.token.gettokentype()
        token_value = self.token.value

        source_pos = self.token.source_pos
        if source_pos is None:
            return "Unexpected %s %s" % (token_type, token_value)

        return "Unexpected %s %s at line %s, column %s" % (
            token_type,
            "'%s'" % (token_value,),
            source_pos.lineno,
            source_pos.colno,
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

pg = ParserGenerator(RULES, cache_id="cycy")

@pg.production("main : program")
def main_program(p):
    return p[0]

@pg.production("program : unit")
def program_function(p):
    return Program([p[0]])

@pg.production("program : unit program")
def program_unit_program(p):
    p[1].add_unit(p[0])
    return p[1]

@pg.production("return_statement : return expr ;")
@pg.production("return_statement : return func_call_statement")
def return_statement(p):
    return ReturnStatement(value=p[1])

@pg.production("unit : function")
@pg.production("unit : prototype")
@pg.production("unit : preprocessor_directive")
def unit(p):
    return p[0]

@pg.production("function : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET block")
def function_void_param(p):
    return Function(
        return_type=p[0],
        name=p[1].getstr(),
        params=[],
        body=p[5]
    )

@pg.production("function : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET block")
def function_with_args(p):
    return Function(
        return_type=p[0],
        name=p[1].getstr(),
        params=p[3].get_items(),
        body=p[5]
    )

@pg.production("prototype : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET ;")
def function_void_param(p):
    return Function(
        return_type=p[0],
        name=p[1].getstr(),
        params=[],
        prototype=True
    )

@pg.production("prototype : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET ;")
def function_with_args(p):
    return Function(
        return_type=p[0],
        name=p[1].getstr(),
        params=p[3].get_items(),
        prototype=True
    )

@pg.production("prototype : type IDENTIFIER LEFT_BRACKET type_list RIGHT_BRACKET ;")
def function_with_args(p):
    return Function(
        return_type=p[0],
        name=p[1].getstr(),
        params=[VariableDeclaration(name=None, vtype=x, value=None) for x in p[3].get_items()],
        prototype=True
    )

@pg.production("arg_decl_list : declaration")
def arg_decl_list_declaration(p):
    return NodeList([p[0]])

@pg.production("arg_decl_list : arg_decl_list , declaration")
def arg_decl_list(p):
    p[0].append(p[2])
    return p[0]

@pg.production("block : LEFT_CURLY_BRACKET statement_list RIGHT_CURLY_BRACKET")
def block_statement_list(p):
    return Block(statements=p[1].get_items())

@pg.production("statement_list : statement")
def statement_list_statement(p):
    return NodeList([p[0]])

@pg.production("statement_list : statement statement_list")
def statement_list_statement_list(p):
    st = NodeList([p[0]])
    st.extend(p[1].get_items())
    return st

@pg.production("statement : return_statement")
@pg.production("statement : expr ;")
@pg.production("statement : declaration ;")
@pg.production("statement : primary_expression ;")
@pg.production("statement : func_call_statement")
@pg.production("statement : while_loop")
@pg.production("statement : for_loop")
@pg.production("statement : if_loop")
@pg.production("statement : assembler ;")
def statement_list_return(p):
    return p[0]

@pg.production("expr : assignment")
def expr_assignment(p):
    return p[0]

@pg.production("assembler : ASM LEFT_BRACKET STRING_LITERAL RIGHT_BRACKET")
def assembler(p):
    return Assembler(instruction=String(p[2].getstr().strip("\"")))

@pg.production("preprocessor_directive : include")
def preprocessor_directive():
    return p[0]

@pg.production("include : INCLUDE STRING_LITERAL")
def include(p):
    return Include(name=p[1].getstr()[1:-1])

@pg.production("if_loop : if LEFT_BRACKET expr RIGHT_BRACKET block")
def if_loop(p):
    return If(condition=p[2], body=p[4])

@pg.production("if_loop : if LEFT_BRACKET expr RIGHT_BRACKET statement")
def if_loop_single_line(p):
    return If(condition=p[2], body=Block(statements=[p[4]]))

@pg.production("while_loop : while LEFT_BRACKET expr RIGHT_BRACKET block")
def while_loop(p):
    return For(condition=p[2], body=p[4])

@pg.production("while_loop : while LEFT_BRACKET expr RIGHT_BRACKET statement")
def while_loop_single_line(p):
    return For(condition=p[2], body=Block(statements=[p[4]]))

@pg.production("for_loop : for LEFT_BRACKET expr ; expr ; expr RIGHT_BRACKET statement")
def for_loop_single_line(p):
    return For(initial=p[2], condition=p[4], increment=p[6], body=Block(statements=[p[8]]))

@pg.production("for_loop : for LEFT_BRACKET expr ; expr ; expr RIGHT_BRACKET block")
def for_loop(p):
    return For(initial=p[2], condition=p[4], increment=p[6], body=p[8])

@pg.production("func_call : IDENTIFIER LEFT_BRACKET param_list RIGHT_BRACKET")
def function_call(p):
    return Call(name=p[0].getstr(), args=p[2].get_items())

@pg.production("func_call_statement : func_call ;")
@pg.production("expr : func_call")
def function_call_expr(p):
    return p[0]

@pg.production("param_list : expr")
def param_list(p):
    return NodeList(items=[p[0]])

@pg.production("assignment : IDENTIFIER = expr")
def assign(p):
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
def binop(p):
    return BinaryOperation(operator=p[1].getstr(), left=p[0], right=p[2])

@pg.production("expr : STRING_LITERAL")
def expr_string(p):
    return String(p[0].getstr().strip("\""))

@pg.production("expr : null")
def expr_null(p):
    return Null()

@pg.production("expr : array LEFT_SQUARE_BRACKET expr RIGHT_SQUARE_BRACKET")
def array_dereference(p):
    return ArrayDereference(array=p[0], index=p[2])

@pg.production("array : IDENTIFIER")
def array_variable(p):
    return Variable(name=p[0].getstr())

@pg.production("declaration : type IDENTIFIER")
def declare_int(p):
    return VariableDeclaration(name=p[1].getstr(), vtype=p[0], value=None)

@pg.production("declaration : type IDENTIFIER LEFT_SQUARE_BRACKET INTEGER_LITERAL RIGHT_SQUARE_BRACKET")
def declare_array(p):
    return VariableDeclaration(name=p[1].getstr(), vtype=Type(base="array", arraylength=int(p[3].getstr()), reference=p[0]))

@pg.production("declaration : type IDENTIFIER = INTEGER_LITERAL")
def declare_assign_int(p):
    return VariableDeclaration(
        name=p[1].getstr(),
        vtype=p[0],
        value=Int32(int(p[3].getstr()))
    )

@pg.production("declaration : type IDENTIFIER = FLOAT_LITERAL")
def declare_assign_float(p):
    return VariableDeclaration(
        name=p[1].getstr(),
        vtype=p[0],
        value=Double(float(p[3].getstr()))
    )

@pg.production("declaration : type IDENTIFIER = STRING_LITERAL")
def declare_assign_string(p):
    return VariableDeclaration(
        name=p[1].getstr(),
        vtype=p[0],
        value=String(p[3].getstr().strip("\""))
    )

@pg.production("type_list : type")
def type_list(p):
    return NodeList([p[0]])

@pg.production("type_list : type_list , type")
def type_list_type(p):
    p[0].append(p[2])
    return p[0]

@pg.production("type : optional_unsigned optional_const core_or_pointer_type")
def type_object(p):
    the_type = p[2]
    assert isinstance(the_type, Type)
    the_type.unsigned = (p[0] == BoolTrue)
    the_type.const = (p[1] == BoolTrue)
    return the_type

@pg.production("optional_const : ")
def const_false(p):
    return BoolFalse

@pg.production("optional_const : CONST")
def const_true(p):
    return BoolTrue

@pg.production("optional_unsigned : ")
def unsigned_false(p):
    return BoolFalse

@pg.production("optional_unsigned : UNSIGNED")
def unsigned_true(p):
    return BoolTrue

@pg.production("core_or_pointer_type : core_type")
def core_type(p):
    return p[0]

@pg.production("core_or_pointer_type : core_or_pointer_type *")
def pointer_type(p):
    return Type(base="pointer", reference=p[0])

@pg.production("core_type : CHAR")
@pg.production("core_type : INT")
@pg.production("core_type : SHORT")
@pg.production("core_type : LONG")
@pg.production("core_type : FLOAT")
@pg.production("core_type : DOUBLE")
def generic_vtype(p):
    return Type(base=p[0].getstr())

@pg.production("core_type : LONG LONG")
def long_long_vtype(p):
    return Type(base='long long')

@pg.production("core_type : LONG DOUBLE")
def long_double_vtype(p):
    return Type(base='long double')

@pg.production("expr : primary_expression ++")
def post_incr(p):
    return PostOperation(operator="++", variable=p[0])

@pg.production("expr : primary_expression --")
def post_incr(p):
    return PostOperation(operator="--", variable=p[0])

@pg.production("expr : ++ primary_expression")
def post_incr(p):
    return PreOperation(operator="++", variable=p[1])

@pg.production("expr : -- primary_expression")
def post_incr(p):
    return PreOperation(operator="--", variable=p[1])

@pg.production("expr : primary_expression")
def expr_const(p):
    return p[0]

@pg.production("primary_expression : const")
@pg.production("primary_expression : IDENTIFIER")
@pg.production("primary_expression : STRING_LITERAL")
@pg.production("primary_expression : LEFT_BRACKET primary_expression RIGHT_BRACKET")
def primary_expression(p):
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
def const(p):
    if p[0].gettokentype() == "INTEGER_LITERAL":
        return Int32(int(p[0].getstr()))
    elif p[0].gettokentype() == "FLOAT_LITERAL":
        return Double(float(p[0].getstr()))
    elif p[0].gettokentype() == "CHAR_LITERAL":
        return Char(p[0].getstr().strip("'"))
    raise AssertionError("Bad token type in const")

@pg.error
def error_handler(token):
    raise ParseError(token=token)

PARSER = pg.build()
