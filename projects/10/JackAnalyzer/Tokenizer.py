import re
import sys
import Types


# noinspection PyAttributeOutsideInit
class Tokenizer:

    def __init__(self, file_stream, file_path):
        self.file = file_stream
        self.file_path = file_path
        self.reset()

    def reset(self):
        self.line_number = -1
        self.current_line = ''
        self.file.seek(0)
        self.advance()

    def __reset_token(self):
        self.type = None
        self.keyword = None
        self.value = None

    def advance(self):
        self.__reset_token()

        while True:
            if self.current_line == '':
                self.__next_line()
                if self.current_line == '':
                    return

            self.current_line = self.current_line.split("//")[0].strip()
            if self.current_line.startswith("/*"):
                while not self.current_line.find("*/"):
                    self.__next_line()
                    if self.current_line == '':
                        return

                self.current_line = self.current_line.split("*/", 1)[1]
                continue

            if self.current_line == '':
                continue

            for keyword in Types.Keywords:
                if self.current_line.startswith(keyword.value):
                    self.type = Types.Tokens.KEYWORD
                    self.keyword = keyword
                    self.value = keyword.value
                    self.current_line = self.current_line[len(keyword.value):]
                    return

            for symbol in Types.symbols:
                if self.current_line.startswith(symbol):
                    self.type = Types.Tokens.SYMBOL
                    self.value = symbol
                    self.current_line = self.current_line[1:]
                    return

            integer_match = re.search(r'^\d+', self.current_line)
            if integer_match is not None:
                self.type = Types.Tokens.INT_CONST
                self.value = integer_match.group(0)
                self.current_line = self.current_line[len(self.value):]
                return

            string_match = re.search(r'^["](.+)["]', self.current_line)
            if string_match is not None:
                self.type = Types.Tokens.INT_CONST
                self.value = string_match.group(1)
                self.current_line = self.current_line[(len(self.value) + 2):]
                return

            identifier_match = re.search(r'^[a-zA-Z_][a-zA-Z0-9_]*', self.current_line)
            if identifier_match is not None:
                self.type = Types.Tokens.IDENTIFIER
                self.value = identifier_match.group(0)
                self.current_line = self.current_line[len(self.value):]
                return

            self.error("Tokenizer : Invalid token starting at '" + self.current_line + "'")

    def __next_line(self):
        self.current_line = self.file.readline()
        self.line_number += 1

    def error(self, error):
        print("Error in " + self.file_path.__str__() + ":" + self.line_number.__str__())
        print(error)
        # sys.exit(2)
