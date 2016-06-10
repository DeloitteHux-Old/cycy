from rply import LexerGenerator

RULES = [
    "INCLUDE",
    "INTEGER_LITERAL",
    "FLOAT_LITERAL",
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
    "if",
    "while",
    "for",
    "ASM",
    "IDENTIFIER",
    "LEFT_SQUARE_BRACKET",
    "RIGHT_SQUARE_BRACKET",
    "LEFT_PARENTHESIS",
    "RIGHT_PARENTHESIS",
    "LEFT_CURLY_BRACE",
    "RIGHT_CURLY_BRACE",
    "||",
    "&&",
    "++",
    "--",
    "==",
    "!=",
    "<=",
    ">=",
    "<",
    ">",
    "=",
    ",",
    "+",
    "-",
    ";",
    "*",
    "/",
    "%",
]
lg = LexerGenerator()
lg.add("INCLUDE", "#include")
lg.add("ASM", "__asm__")
lg.add("ASM", "asm")
lg.add("FLOAT_LITERAL", "\d+\.\d+")
lg.add("INTEGER_LITERAL", "\d+")
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
lg.add("if", "if")
lg.add("while", "while")
lg.add("for", "for")
lg.add("IDENTIFIER", "[_a-zA-Z][_a-zA-Z0-9]*")
lg.add("LEFT_SQUARE_BRACKET", "\[")
lg.add("RIGHT_SQUARE_BRACKET", "\]")
lg.add("LEFT_PARENTHESIS", "\(")
lg.add("RIGHT_PARENTHESIS", "\)")
lg.add("LEFT_CURLY_BRACE", "{")
lg.add("RIGHT_CURLY_BRACE", "}")
lg.add("||", "\|\|")
lg.add("&&", "&&")
lg.add("++", "\+\+")
lg.add("--", "--")
lg.add("==", "==")
lg.add("!=", "!=")
lg.add("<=", "<=")
lg.add(">=", ">=")
lg.add("<", "<")
lg.add(">", ">")
lg.add("=", "=")
lg.add(",", ",")
lg.add("+", "\+")
lg.add("-", "-")
lg.add(";", ";")
lg.add("*", "\*")
lg.add("/", "/")
lg.add("%", "%")
lg.ignore("\s+")
lexer = lg.build()
