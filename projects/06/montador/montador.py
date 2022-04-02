#!/usr/local/bin/python3

import sys
from pathlib import Path

import codes
import parser


def inputError(error):
    print(error)
    print("Correct usage : montador.py <input-file>")
    sys.exit(2)


if len(sys.argv) < 2:
    inputError("Missing input file")

inputFilePath = Path(sys.argv[1])
if not inputFilePath.is_file:
    inputError("Invalid input file")

parser = parser.Parser(inputFilePath)

outputFilePath = str(inputFilePath.resolve()).replace(".asm", ".hack")
if not outputFilePath.endswith(".hack"):
    outputFilePath += ".hack"
outputFilePath = Path(outputFilePath)
outputFile = open(outputFilePath, "w")


def register(n):
    return "R" + str(n)


defaultSymbols = ["SP", "LCL", "ARG", "THIS", "THAT"]
registerSymbols = list(map(register, list(range(16))))
symbols = {}
symbols.update({key: idx for idx, key in enumerate(defaultSymbols)})
symbols.update({key: idx for idx, key in enumerate(registerSymbols)})
symbols.update({"SCREEN": 16384, "KBD": 24576})

nextRAM = 16
nextROM = 0

while parser.hasMoreCommands():
    if parser.commandType == codes.CommandType.L_COMMAND:
        symbols[parser.symbol] = nextROM
    else:
        nextROM += 1
    parser.advance()
    continue

parser.resetFileCursor()
parser.advance()


def getOrAddSymbolAddress(symbol):
    global nextRAM
    if symbol in symbols:
        return symbols[symbol]
    else:
        symbols[symbol] = nextRAM
        nextRAM += 1
        return symbols[symbol]


while parser.hasMoreCommands():

    if parser.commandType == codes.CommandType.A_COMMAND:
        address = int(parser.symbol) if str(parser.symbol).isdigit() else getOrAddSymbolAddress(parser.symbol)
        outputFile.write("0" + '{:015b}'.format(address) + "\n")

    elif parser.commandType == codes.CommandType.C_COMMAND:
        outputFile.write("111" + codes.comp(parser.comp) + codes.dest(parser.dest) + codes.jump(parser.jump) + "\n")

    parser.advance()

outputFile.close()
