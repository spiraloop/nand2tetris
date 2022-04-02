import codes
import sys


class Parser:
    def __init__(self, inputFilePath):
        self.currentLine = None
        self.commandType = None
        self.inputFile = open(inputFilePath, "r")
        self.line_number = -1
        self.symbol = ""
        self.dest = ""
        self.comp = ""
        self.jump = ""
        self.advance()

    def __del__(self):
        self.inputFile.close()

    def resetFileCursor(self):
        self.inputFile.seek(0)

    def hasMoreCommands(self):
        return self.currentLine != ''

    def parserError(self):
        print("Parser error in the line " + self.line_number + " : " + self.currentLine.strip())
        sys.exit(2)

    def advance(self):
        while True:

            self.line_number += 1
            self.currentLine = self.inputFile.readline()
            if self.currentLine == '':
                return

            line = self.currentLine.split("//")[0].strip()

            if line == '':
                continue

            self.dest = ""
            self.comp = ""
            self.jump = ""

            if line.startswith("@"):
                self.commandType = codes.CommandType.A_COMMAND
                self.symbol = line[1:]
            elif line.startswith('('):
                if not line.endswith(')'):
                    self.parserError()
                self.commandType = codes.CommandType.L_COMMAND
                self.symbol = line[1:-1]
            else:
                self.commandType = codes.CommandType.C_COMMAND
                command = line.split(';')
                if len(command) == 2:
                    self.jump = command[1]
                    line = command[0]
                command = line.split('=')
                if len(command) == 2:
                    self.comp = command[1]
                    self.dest = command[0]
                else:
                    self.comp = command[0]

            return
