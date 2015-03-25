from rply import LexerGenerator

RULES = [
    "INTEGER",
    "CHAR",
    "STRING",
    "INT32",
    "IDENTIFIER",
    "LEFT_SQUARE_BRACKET",
    "RIGHT_SQUARE_BRACKET",
    "=",
    "!=",
    "++",
]
lg = LexerGenerator()
lg.add("INTEGER", "\d+"),
lg.add("CHAR", "'.'"),
lg.add("STRING", "\".*\""),
lg.add("INT32", "int"),
lg.add("IDENTIFIER", "[_a-zA-Z][_a-zA-Z0-9]*"),
lg.add("LEFT_SQUARE_BRACKET", "\["),
lg.add("RIGHT_SQUARE_BRACKET", "\]"),
lg.add("=", "="),
lg.add("!=", "!="),
lg.add("++", "\+\+")
lg.ignore("\s+")
lexer = lg.build()


def lexer_run(source):
    return lexer.lex(source)
