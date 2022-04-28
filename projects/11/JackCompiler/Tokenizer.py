import re
import Types


# noinspection PyAttributeOutsideInit
class Tokenizer:

	def __init__(self, file_stream, file_path):
		self.file = file_stream
		self.file_path = file_path
		self.reset()

	def reset(self):
		self.line_number = 0
		self.current_line = ''
		self.file.seek(0)
		self.advance()

	def __reset_token(self):
		self.type = None
		self.keyword = None
		self.value = None

	def get_token(self):
		class Token:
			type = self.type
			keyword = self.keyword
			value = self.value
			line_number = self.line_number

		return Token

	def advance(self):
		self.__reset_token()

		while True:
			if self.current_line == '':
				self.__next_line()
				if self.current_line == '':
					return

			self.current_line = self.current_line.split("//")[0].strip()
			if self.current_line.startswith("/*"):
				end = self.current_line.find("*/")
				while end == -1:
					self.__next_line()
					if self.current_line == '':
						self.error("Could find the end of the comment block")
						return
					end = self.current_line.find("*/")

				self.current_line = self.current_line[end+2:]
				continue

			if self.current_line == '':
				continue

			keyword_match = re.search(r'^[a-z]+', self.current_line)
			if keyword_match is not None:
				word = keyword_match.group(0)
				for keyword in Types.Keywords:
					if word == keyword.value:
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
				self.type = Types.Tokens.STRING_CONST
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
