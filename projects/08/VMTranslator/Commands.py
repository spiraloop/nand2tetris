from enum import Enum


class CommandTypes(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


command_type_map = {
    'push': CommandTypes.C_PUSH,
    'pop': CommandTypes.C_POP,
    'add': CommandTypes.C_ARITHMETIC,
    'sub': CommandTypes.C_ARITHMETIC,
    'neg': CommandTypes.C_ARITHMETIC,
    'eq': CommandTypes.C_ARITHMETIC,
    'gt': CommandTypes.C_ARITHMETIC,
    'lt': CommandTypes.C_ARITHMETIC,
    'and': CommandTypes.C_ARITHMETIC,
    'or': CommandTypes.C_ARITHMETIC,
    'not': CommandTypes.C_ARITHMETIC,
    'label': CommandTypes.C_LABEL,
    'goto': CommandTypes.C_GOTO,
    'if-goto': CommandTypes.C_IF,
    'function': CommandTypes.C_FUNCTION,
    'return': CommandTypes.C_RETURN,
    'call': CommandTypes.C_CALL,
}


class SegmentType(Enum):
    POINTER = 0
    REFERENCE = 1


segments = {
    'argument',
    'local',
    'static',
    'constant',
    'this',
    'that',
    'pointer',
    'temp',
}

segment_label_type_map = {
    'local': ('LCL', SegmentType.POINTER),
    'argument': ('ARG', SegmentType.POINTER),
    'this': ('THIS', SegmentType.POINTER),
    'that': ('THAT', SegmentType.POINTER),
    'temp': ('R5', SegmentType.REFERENCE),
    'pointer': ('THIS', SegmentType.REFERENCE),
}
