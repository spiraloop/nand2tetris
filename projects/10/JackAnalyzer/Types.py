from enum import Enum


class Tokens(Enum):
    KEYWORD = "keyword"
    SYMBOL = "symbol"
    IDENTIFIER = "identifier"
    INT_CONST = "integerConstant"
    STRING_CONST = "stringConstant"


class Keywords(Enum):
    CLASS = "class"
    CONSTRUCTOR = "constructor"
    FUNCTION = "function"
    METHOD = "method"
    FIELD = "field"
    STATIC = "static"
    VAR = "var"
    INT = "int"
    CHAR = "char"
    BOOLEAN = "boolean"
    VOID = "void"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    THIS = "this"
    LET = "let"
    DO = "do"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"


symbols = '{}()[].,;+-*/&|<>=~'