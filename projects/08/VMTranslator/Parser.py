import sys
from pathlib import Path

import Commands


class Parser:
    def __init__(self, file_path):
        self.line_number = -1
        self.currentLine = None
        self.command_type = None
        self.arg1 = None
        self.arg2 = None
        self.file_path = Path(file_path)
        self.file = open(self.file_path, "r")
        self.advance()

    def advance(self):
        while True:
            self.line_number += 1
            self.currentLine = self.file.readline()
            if self.currentLine == '':
                return

            line = self.currentLine.split("//")[0].strip()

            if line == '':
                continue

            self.arg1 = None
            self.arg2 = None

            tokens = line.split(' ')
            cmd = tokens.pop(0)
            if cmd not in Commands.command_type_map:
                self.error("Invalid command '" + line + "'")

            self.command_type = Commands.command_type_map[cmd]

            if self.command_type == Commands.CommandTypes.C_PUSH or self.command_type == Commands.CommandTypes.C_POP:
                if len(tokens) != 2:
                    self.error("Invalid command '" + line + "'")

                self.arg1 = tokens.pop(0)
                self.arg2 = tokens.pop(0)

                if not Commands.segments.__contains__(self.arg1):
                    self.error("Invalid segment '" + line + "'")
                if not self.arg2.isdigit():
                    self.error("Invalid index '" + line + "'")
                if self.command_type == Commands.CommandTypes.C_POP and self.arg1 == "constant":
                    self.error("Meaningless command '" + line + "'")
                if self.arg1 == "pointer" and int(self.arg2) > 1:
                    self.error("Pointer index out of range [0-1]'" + line + "'")
                if self.arg1 == "temp" and int(self.arg2) > 7:
                    self.error("Temp index out of range [0-7]'" + line + "'")

            elif self.command_type == Commands.CommandTypes.C_ARITHMETIC:
                self.arg1 = cmd

            return

    def has_more_commands(self):
        return self.currentLine != ''

    def error(self, error):
        print("Parser error in " + self.file_path.resolve().__str__() + ":" + self.line_number.__str__())
        print(error)
        sys.exit(2)
