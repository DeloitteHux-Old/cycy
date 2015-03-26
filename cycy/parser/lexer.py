from rply import LexerGenerator

RULES = [
    "INTEGER",
    "CHAR",
    "STRING",
    "INT32",
    "CHAR",
    "CONST",
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
    "!=",
    "++",
    "+",
    ";",
    "*",
]
lg = LexerGenerator()
lg.add("INTEGER", "\d+")
lg.add("CHAR", "'\\\\?.'")
lg.add("STRING", "\".*\"")
lg.add("INT32", "int")
lg.add("CHAR", "char")
lg.add("null", "NULL")
lg.add("CONST", "const")
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
lg.add("!=", "!=")
lg.add("++", "\+\+")
lg.add("+", "\+")
lg.add(";", ";")
lg.add("*", "\*")
lg.ignore("\s+")
lexer = lg.build()


def lexer_run(source):
    return lexer.lex(source)
