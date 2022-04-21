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

            self.currentLine = self.currentLine.split("//")[0].strip()

            if self.currentLine == '':
                continue

            self.arg1 = None
            self.arg2 = None

            tokens = self.currentLine.split(' ')
            cmd = tokens.pop(0)
            if cmd not in Commands.command_type_map:
                self.__error("Unknown command")

            self.command_type = Commands.command_type_map[cmd]

            if self.command_type == Commands.CommandTypes.C_PUSH or self.command_type == Commands.CommandTypes.C_POP:
                self.__assert_token_count(tokens, 2)

                self.arg1 = tokens.pop(0)
                self.arg2 = tokens.pop(0)

                if not Commands.segments.__contains__(self.arg1):
                    self.__error("Invalid segment")
                if not self.arg2.isdigit():
                    self.__error("Invalid index")
                if self.command_type == Commands.CommandTypes.C_POP and self.arg1 == "constant":
                    self.__error("Meaningless command")
                if self.arg1 == "pointer" and int(self.arg2) > 1:
                    self.__error("Pointer index out of range [0-1]")
                if self.arg1 == "temp" and int(self.arg2) > 7:
                    self.__error("Temp index out of range [0-7]")

            elif self.command_type == Commands.CommandTypes.C_ARITHMETIC:
                self.__assert_token_count(tokens, 0)
                self.arg1 = cmd

            elif self.command_type == Commands.CommandTypes.C_LABEL:
                self.__assert_token_count(tokens, 1)
                self.arg1 = tokens.pop(0)
                self.__assert_valid_name(self.arg1)

            elif self.command_type == Commands.CommandTypes.C_GOTO or self.command_type == Commands.CommandTypes.C_IF:
                self.__assert_token_count(tokens, 1)
                self.arg1 = tokens.pop(0)
                self.__assert_valid_name(self.arg1)

            elif self.command_type == Commands.CommandTypes.C_FUNCTION:
                self.__assert_token_count(tokens, 2)
                self.arg1 = tokens.pop(0)
                self.arg2 = tokens.pop(0)
                self.__assert_valid_name(self.arg1)
                if not self.arg2.isdigit():
                    self.__error("Invalid number of arguments")

            elif self.command_type == Commands.CommandTypes.C_RETURN:
                self.__assert_token_count(tokens, 0)

            elif self.command_type == Commands.CommandTypes.C_CALL:
                self.__assert_token_count(tokens, 2)
                self.arg1 = tokens.pop(0)
                self.arg2 = tokens.pop(0)
                self.__assert_valid_name(self.arg1)
                if not self.arg2.isdigit():
                    self.__error("Invalid number of variables")

            return

    def has_more_commands(self):
        return self.currentLine != ''

    def __assert_token_count(self, tokens_count, required_count):
        if len(tokens_count) != required_count:
            self.__error("Invalid number of tokens (got " + tokens_count + ", expected " + required_count + "")

    def __assert_valid_name(self, label):
        if label[0].isdigit():
            self.__error("Invalid label name")

    def __error(self, error):
        print("Parser error in " + self.file_path.resolve().__str__() + ":" + self.line_number.__str__())
        print(error + " '" + self.currentLine + "'")
        sys.exit(2)
