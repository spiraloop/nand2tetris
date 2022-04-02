from enum import Enum


class CommandType(Enum):
    A_COMMAND = 0
    C_COMMAND = 1
    L_COMMAND = 2


def dest(mnemonic: str):
    result = [0, 0, 0]
    if mnemonic.find("A") != -1:
        result[0] = 1
    if mnemonic.find("D") != -1:
        result[1] = 1
    if mnemonic.find("M") != -1:
        result[2] = 1
    return "".join(map(str, result))


def jump(mnemonic: str):
    if mnemonic == '':
        return "000"
    elif mnemonic == 'JGT':
        return "001"
    elif mnemonic == 'JEQ':
        return "010"
    elif mnemonic == 'JGE':
        return "011"
    elif mnemonic == 'JLT':
        return "100"
    elif mnemonic == 'JNE':
        return "101"
    elif mnemonic == 'JLE':
        return "110"
    elif mnemonic == 'JMP':
        return "111"


def comp(mnemonic: str):
    if mnemonic == '0':
        return "0101010"
    elif mnemonic == '1':
        return "0111111"
    elif mnemonic == '-1':
        return "0111010"
    elif mnemonic == 'D':
        return "0001100"
    elif mnemonic == 'A':
        return "0110000"
    elif mnemonic == 'M':
        return "1110000"
    elif mnemonic == '!D':
        return "0001101"
    elif mnemonic == '!A':
        return "0110001"
    elif mnemonic == '!M':
        return "1110001"
    elif mnemonic == '-D':
        return "0001111"
    elif mnemonic == '-A':
        return "0110011"
    elif mnemonic == '-M':
        return "1110011"
    elif mnemonic == 'D+1':
        return "0011111"
    elif mnemonic == 'A+1':
        return "0110111"
    elif mnemonic == 'M+1':
        return "1110111"
    elif mnemonic == 'D-1':
        return "0001110"
    elif mnemonic == 'A-1':
        return "0110010"
    elif mnemonic == 'M-1':
        return "1110010"
    elif mnemonic == 'D+A':
        return "0000010"
    elif mnemonic == 'D+M':
        return "1000010"
    elif mnemonic == 'D-A':
        return "0010011"
    elif mnemonic == 'D-M':
        return "1010011"
    elif mnemonic == 'A-D':
        return "0000111"
    elif mnemonic == 'M-D':
        return "1000111"
    elif mnemonic == 'D&A':
        return "0000000"
    elif mnemonic == 'D&M':
        return "1000000"
    elif mnemonic == 'D|A':
        return "0010101"
    elif mnemonic == 'D|M':
        return "1010101"
