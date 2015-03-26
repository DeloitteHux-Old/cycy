from rply import LexerGenerator

RULES = [
    "INTEGER",
    "CHAR_LITERAL",
    "STRING_LITERAL",
    "CHAR",
    "SHORT",
    "INT",
    "LONG",
    "FLOAT",
    "DOUBLE",
    "CONST",
    "UNSIGNED",
    "null",
    "return",
    "void",
    "while",
    "IDENTIFIER",
    "LEFT_SQUARE_BRACKET",
    "RIGHT_SQUARE_BRACKET",
    "LEFT_BRACKET",
    "RIGHT_BRACKET",
    "LEFT_CURLY_BRACKET",
    "RIGHT_CURLY_BRACKET",
    "=",
    ",",
    "!=",
    "<=",
    "++",
    "+",
    "-",
    ";",
    "*",
]
lg = LexerGenerator()
lg.add("INTEGER", "\d+")
lg.add("CHAR_LITERAL", "'\\\\?.'")
lg.add("STRING_LITERAL", "\".*\"")
lg.add("CHAR", "char")
lg.add("SHORT", "short")
lg.add("INT", "int")
lg.add("LONG", "long")
lg.add("FLOAT", "float")
lg.add("DOUBLE", "double")
lg.add("null", "NULL")
lg.add("CONST", "const")
lg.add("UNSIGNED", "unsigned")
lg.add("return", "return")
lg.add("void", "void")
lg.add("while", "while")
lg.add("IDENTIFIER", "[_a-zA-Z][_a-zA-Z0-9]*")
lg.add("LEFT_SQUARE_BRACKET", "\[")
lg.add("RIGHT_SQUARE_BRACKET", "\]")
lg.add("LEFT_BRACKET", "\(")
lg.add("RIGHT_BRACKET", "\)")
lg.add("LEFT_CURLY_BRACKET", "{")
lg.add("RIGHT_CURLY_BRACKET", "}")
lg.add("=", "=")
lg.add(",", ",")
lg.add("!=", "!=")
lg.add("<=", "<=")
lg.add("++", "\+\+")
lg.add("+", "\+")
lg.add("-", "-")
lg.add(";", ";")
lg.add("*", "\*")
lg.ignore("\s+")
lexer = lg.build()


def lexer_run(source):
    return lexer.lex(source)
