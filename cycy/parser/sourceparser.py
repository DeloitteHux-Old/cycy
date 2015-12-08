from characteristic import Attribute, attributes
from rply import ParserGenerator
from rply.errors import LexingError as _RPlyLexingError

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
from cycy.parser.lexer import RULES, lexer


class LexingError(CyCyError):
    def __init__(self, source_pos, message):
        self.message = message
        self.source_pos = source_pos

    def __str__(self):
        return "Lexer failed at %s (message: %s)" % (
            self.source_pos, self.message,
        )


class ParseError(CyCyError):
    def __init__(self, token, source):
        self.token = token
        self.source = source

    def __str__(self):
        token_type = self.token.gettokentype()
        token_value = self.token.value

        source_pos = self.token.source_pos
        if source_pos is None:
            return "Unexpected %s %s" % (token_type, token_value)

        line, column = source_pos.lineno, source_pos.colno

        return (
            "\n" +
            self._hint(line_number=line - 1, column_number=column - 1) +
                "Unexpected %s %s at line %s, column %s" % (
                token_type,
                "'%s'" % (token_value,),
                source_pos.lineno,
                source_pos.colno,
            )
        )

    def _hint(self, line_number, column_number):
        """
        Find a hint in the source at the given line and column.

        """

        line = self.source.splitlines(True)[line_number]
        return line + " " * column_number + "^\n"


class UnexpectedEnd(ParseError):
    """
    There was an unexpected end in the input.

    """


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


@attributes(
    [
        Attribute(name="lexer", exclude_from_repr=True),
        Attribute(name="preprocessor", exclude_from_repr=True),
    ],
    apply_with_init=False,
)
class Parser(object):
    def __init__(self, preprocessor, lexer=lexer):
        self.preprocessor = preprocessor
        self.lexer = lexer

    def parse(self, source):
        tokens = self.lexer.lex(source)
        preprocessed = self.preprocessor.preprocessed(
            tokens=tokens, parser=self,
        )

        # Nasty -- saved in case it's needed for a parsing error
        self.source = source
        try:
            program = self._parser.parse(preprocessed, state=self)
        except _RPlyLexingError as error:
            raise LexingError(
                source_pos=error.source_pos,
                message=error.message,
            )

        assert isinstance(program, Program)
        return program

    _pg = ParserGenerator(RULES, cache_id="cycy")

    @_pg.production("main : program")
    def main_program(self, p):
        return p[0]

    @_pg.production("program : unit")
    def program_function(self, p):
        return Program([p[0]])

    @_pg.production("program : unit program")
    def program_unit_program(self, p):
        p[1].add_unit(p[0])
        return p[1]

    @_pg.production("return_statement : return expr ;")
    def return_statement(self, p):
        return ReturnStatement(value=p[1])

    @_pg.production("unit : function")
    @_pg.production("unit : prototype")
    @_pg.production("unit : preprocessor_directive")
    def unit(self, p):
        return p[0]

    @_pg.production("function : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET block")
    def function_void_param(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[],
            body=p[5]
        )

    @_pg.production("function : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET block")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=p[3].get_items(),
            body=p[5]
        )

    @_pg.production("prototype : type IDENTIFIER LEFT_BRACKET void RIGHT_BRACKET ;")
    def function_void_param(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[],
            prototype=True
        )

    @_pg.production("prototype : type IDENTIFIER LEFT_BRACKET arg_decl_list RIGHT_BRACKET ;")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=p[3].get_items(),
            prototype=True
        )

    @_pg.production("prototype : type IDENTIFIER LEFT_BRACKET type_list RIGHT_BRACKET ;")
    def function_with_args(self, p):
        return Function(
            return_type=p[0],
            name=p[1].getstr(),
            params=[VariableDeclaration(name=None, vtype=x, value=None) for x in p[3].get_items()],
            prototype=True
        )

    @_pg.production("arg_decl_list : declaration")
    def arg_decl_list_declaration(self, p):
        return NodeList([p[0]])

    @_pg.production("arg_decl_list : arg_decl_list , declaration")
    def arg_decl_list(self, p):
        p[0].append(p[2])
        return p[0]

    @_pg.production("block : LEFT_CURLY_BRACKET statement_list RIGHT_CURLY_BRACKET")
    def block_statement_list(self, p):
        return Block(statements=p[1].get_items())

    @_pg.production("statement_list : statement")
    def statement_list_statement(self, p):
        return NodeList([p[0]])

    @_pg.production("statement_list : statement statement_list")
    def statement_list_statement_list(self, p):
        st = NodeList([p[0]])
        st.extend(p[1].get_items())
        return st

    @_pg.production("statement : return_statement")
    @_pg.production("statement : expr ;")
    @_pg.production("statement : declaration ;")
    @_pg.production("statement : primary_expression ;")
    @_pg.production("statement : func_call_statement")
    @_pg.production("statement : while_loop")
    @_pg.production("statement : for_loop")
    @_pg.production("statement : if_loop")
    @_pg.production("statement : assembler ;")
    def statement_list_return(self, p):
        return p[0]

    @_pg.production("expr : assignment")
    def expr_assignment(self, p):
        return p[0]

    @_pg.production("assembler : ASM LEFT_BRACKET STRING_LITERAL RIGHT_BRACKET")
    def assembler(self, p):
        return Assembler(instruction=String(p[2].getstr().strip("\"")))

    @_pg.production("preprocessor_directive : include")
    def preprocessor_directive(self, p):
        return p[0]

    @_pg.production("include : INCLUDE STRING_LITERAL")
    def include(self, p):
        return Include(name=p[1].getstr().strip('"'))

    @_pg.production("if_loop : if LEFT_BRACKET expr RIGHT_BRACKET block")
    def if_loop(self, p):
        return If(condition=p[2], body=p[4])

    @_pg.production("if_loop : if LEFT_BRACKET expr RIGHT_BRACKET statement")
    def if_loop_single_line(self, p):
        return If(condition=p[2], body=Block(statements=[p[4]]))

    @_pg.production("while_loop : while LEFT_BRACKET expr RIGHT_BRACKET block")
    def while_loop(self, p):
        return For(condition=p[2], body=p[4])

    @_pg.production("while_loop : while LEFT_BRACKET expr RIGHT_BRACKET statement")
    def while_loop_single_line(self, p):
        return For(condition=p[2], body=Block(statements=[p[4]]))

    @_pg.production("for_loop : for LEFT_BRACKET expr ; expr ; expr RIGHT_BRACKET statement")
    def for_loop_single_line(self, p):
        return For(initial=p[2], condition=p[4], increment=p[6], body=Block(statements=[p[8]]))

    @_pg.production("for_loop : for LEFT_BRACKET expr ; expr ; expr RIGHT_BRACKET block")
    def for_loop(self, p):
        return For(initial=p[2], condition=p[4], increment=p[6], body=p[8])

    @_pg.production("func_call : IDENTIFIER LEFT_BRACKET param_list RIGHT_BRACKET")
    def function_call(self, p):
        return Call(name=p[0].getstr(), args=p[2].get_items())

    @_pg.production("func_call_statement : func_call ;")
    @_pg.production("expr : func_call")
    def function_call_expr(self, p):
        return p[0]

    @_pg.production("param_list : expr")
    @_pg.production("param_list : ")
    def param_list(self, p):
        return NodeList(items=[p[0]] if p else None)

    @_pg.production("assignment : IDENTIFIER = expr")
    def assign(self, p):
        return Assignment(left=Variable(p[0].getstr()), right=p[2])

    @_pg.production("expr : expr - expr")
    @_pg.production("expr : expr + expr")
    @_pg.production("expr : expr * expr")
    @_pg.production("expr : expr / expr")
    @_pg.production("expr : expr % expr")
    @_pg.production('expr : expr || expr')
    @_pg.production('expr : expr && expr')
    @_pg.production('expr : expr == expr')
    @_pg.production('expr : expr != expr')
    @_pg.production("expr : expr <= expr")
    @_pg.production("expr : expr >= expr")
    @_pg.production("expr : expr < expr")
    @_pg.production("expr : expr > expr")
    def binop(self, p):
        return BinaryOperation(operator=p[1].getstr(), left=p[0], right=p[2])

    @_pg.production("expr : STRING_LITERAL")
    def expr_string(self, p):
        return String(p[0].getstr().strip("\""))

    @_pg.production("expr : null")
    def expr_null(self, p):
        return Null()

    @_pg.production("expr : array LEFT_SQUARE_BRACKET expr RIGHT_SQUARE_BRACKET")
    def array_dereference(self, p):
        return ArrayDereference(array=p[0], index=p[2])

    @_pg.production("array : IDENTIFIER")
    def array_variable(self, p):
        return Variable(name=p[0].getstr())

    @_pg.production("declaration : type IDENTIFIER")
    def declare_int(self, p):
        return VariableDeclaration(name=p[1].getstr(), vtype=p[0], value=None)

    @_pg.production("declaration : type IDENTIFIER LEFT_SQUARE_BRACKET INTEGER_LITERAL RIGHT_SQUARE_BRACKET")
    def declare_array(self, p):
        return VariableDeclaration(name=p[1].getstr(), vtype=Type(base="array", arraylength=int(p[3].getstr()), reference=p[0]))

    @_pg.production("declaration : type IDENTIFIER = INTEGER_LITERAL")
    def declare_assign_int(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=Int32(int(p[3].getstr()))
        )

    @_pg.production("declaration : type IDENTIFIER = FLOAT_LITERAL")
    def declare_assign_float(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=Double(float(p[3].getstr()))
        )

    @_pg.production("declaration : type IDENTIFIER = STRING_LITERAL")
    def declare_assign_string(self, p):
        return VariableDeclaration(
            name=p[1].getstr(),
            vtype=p[0],
            value=String(p[3].getstr().strip("\""))
        )

    @_pg.production("type_list : type")
    def type_list(self, p):
        return NodeList([p[0]])

    @_pg.production("type_list : type_list , type")
    def type_list_type(self, p):
        p[0].append(p[2])
        return p[0]

    @_pg.production("type : optional_unsigned optional_const core_or_pointer_type")
    def type_object(self, p):
        the_type = p[2]
        assert isinstance(the_type, Type)
        the_type.unsigned = (p[0] == BoolTrue)
        the_type.const = (p[1] == BoolTrue)
        return the_type

    @_pg.production("optional_const : ")
    def const_false(self, p):
        return BoolFalse

    @_pg.production("optional_const : CONST")
    def const_true(self, p):
        return BoolTrue

    @_pg.production("optional_unsigned : ")
    def unsigned_false(self, p):
        return BoolFalse

    @_pg.production("optional_unsigned : UNSIGNED")
    def unsigned_true(self, p):
        return BoolTrue

    @_pg.production("core_or_pointer_type : core_type")
    def core_type(self, p):
        return p[0]

    @_pg.production("core_or_pointer_type : core_or_pointer_type *")
    def pointer_type(self, p):
        return Type(base="pointer", reference=p[0])

    @_pg.production("core_type : CHAR")
    @_pg.production("core_type : INT")
    @_pg.production("core_type : SHORT")
    @_pg.production("core_type : LONG")
    @_pg.production("core_type : FLOAT")
    @_pg.production("core_type : DOUBLE")
    def generic_vtype(self, p):
        return Type(base=p[0].getstr())

    @_pg.production("core_type : LONG LONG")
    def long_long_vtype(self, p):
        return Type(base='long long')

    @_pg.production("core_type : LONG DOUBLE")
    def long_double_vtype(self, p):
        return Type(base='long double')

    @_pg.production("expr : primary_expression ++")
    def post_incr(self, p):
        return PostOperation(operator="++", variable=p[0])

    @_pg.production("expr : primary_expression --")
    def post_incr(self, p):
        return PostOperation(operator="--", variable=p[0])

    @_pg.production("expr : ++ primary_expression")
    def post_incr(self, p):
        return PreOperation(operator="++", variable=p[1])

    @_pg.production("expr : -- primary_expression")
    def post_incr(self, p):
        return PreOperation(operator="--", variable=p[1])

    @_pg.production("expr : primary_expression")
    def expr_const(self, p):
        return p[0]

    @_pg.production("primary_expression : const")
    @_pg.production("primary_expression : IDENTIFIER")
    @_pg.production("primary_expression : STRING_LITERAL")
    @_pg.production("primary_expression : LEFT_BRACKET primary_expression RIGHT_BRACKET")
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

    @_pg.production("const : FLOAT_LITERAL")
    @_pg.production("const : INTEGER_LITERAL")
    @_pg.production("const : CHAR_LITERAL")
    def const(self, p):
        if p[0].gettokentype() == "INTEGER_LITERAL":
            return Int32(int(p[0].getstr()))
        elif p[0].gettokentype() == "FLOAT_LITERAL":
            return Double(float(p[0].getstr()))
        elif p[0].gettokentype() == "CHAR_LITERAL":
            return Char(p[0].getstr().strip("'"))
        raise AssertionError("Bad token type in const")

    @_pg.error
    def error_handler(self, token):
        is_unexpected_end = token.gettokentype() == "$end"
        if is_unexpected_end:
            ParseException = UnexpectedEnd
        else:
            ParseException = ParseError
        raise ParseException(token=token, source=self.source)

    _parser = _pg.build()
