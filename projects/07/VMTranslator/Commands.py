from enum import Enum


class CommandTypes(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2


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
