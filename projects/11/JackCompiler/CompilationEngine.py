import Types
import SymbolTable


class VMWriter:
	def __init__(self, file):
		self.file = file

	def label(self, name):
		self.file.write("label " + name + "\n")

	def push_constant(self, constant):
		self.file.write("push constant " + str(constant) + "\n")

	def command(self, command):
		self.file.write(command + "\n")

	def command_symbol(self, command, symbol):
		self.file.write(command + " " + Types.kindToPointer[symbol.kind] + " " + str(symbol.index) + "\n")

	def call(self, subroutine, arguments_count):
		self.file.write("call " + subroutine + " " + str(arguments_count) + "\n")


class CompilationError(Exception):
	def __init__(self, message, token):
		self.message = message
		self.token = token


class CompilationEngine:
	def __init__(self, token_list, output_file):
		self.token_list = token_list
		self.token_list_size = len(token_list)
		self.token_cursor = 0
		self.current_token = token_list[self.token_cursor]
		self.vm_writer = VMWriter(output_file)

		self.symbol_table = SymbolTable.SymbolTable()
		self.class_name = None
		self.subroutine_name = None
		self.subroutine_type = None
		self.scope_counters = {}

	def compile(self):
		self.class_()

	def advance(self):
		self.token_cursor += 1
		if self.token_cursor > self.token_list_size:
			self.error("Unexpected end of file")

		if self.token_cursor < self.token_list_size:
			self.current_token = self.token_list[self.token_cursor]

	def class_(self):
		self.keyword("class")

		self.class_name = self.identifier()

		self.symbol('{')

		self.class_variables()
		self.class_subroutines()

		self.symbol('}')

	def class_variables(self):
		declaration_types = ["static", "field"]
		while self.match(Types.Tokens.KEYWORD, declaration_types):
			kind = self.keyword(declaration_types)
			self.variable_list(kind)
			self.symbol(";")

	def variable_list(self, kind):
		type_ = self.type_()
		name = self.identifier()
		count = 1
		self.symbol_table.define(name, type_, kind)
		while self.match(Types.Tokens.SYMBOL, [","]):
			self.symbol(",")
			name = self.identifier()
			count += 1
			self.symbol_table.define(name, type_, kind)
		return count

	routine_types = ["constructor", "function", "method"]

	def class_subroutines(self):
		while self.match(Types.Tokens.KEYWORD, self.routine_types):
			self.subroutine()

	def subroutine(self):
		routine_type = self.keyword(self.routine_types)

		if self.match(Types.Tokens.KEYWORD, ["void"]):
			self.subroutine_type = self.keyword("void")
		else:
			self.subroutine_type = self.type_()

		self.subroutine_name = self.identifier()
		self.symbol_table.start_subroutine()
		self.reset_scope_counter()

		if routine_type == "method":
			self.symbol_table.define("this", self.subroutine_type, "arg")

		self.symbol("(")
		self.parameter_list()
		self.symbol(")")

		self.symbol("{")
		subroutine_var_count = self.subroutine_variables()
		self.vm_writer.command("function " + self.class_name + "." + self.subroutine_name + " " + str(subroutine_var_count))
		if routine_type == "constructor":
			class_var_count = self.symbol_table.var_count("field")
			self.vm_writer.push_constant(class_var_count)
			self.vm_writer.call("Memory.alloc", 1)
			self.vm_writer.command("pop pointer 0")
		elif routine_type == "method":
			self.vm_writer.command("push argument 0")
			self.vm_writer.command("pop pointer 0")
		self.statements()
		self.symbol("}")

	def subroutine_variables(self):
		count = 0
		while self.match(Types.Tokens.KEYWORD, ["var"]):
			kind = self.keyword("var")
			count += self.variable_list(kind)
			self.symbol(";")
		return count

	def match(self, token_type, values=None):
		return self.match_(self.current_token, token_type, values)

	def match_next(self, token_type, values=None):
		next_cursor = self.token_cursor + 1
		if next_cursor > self.token_list_size:
			return False
		return self.match_(self.token_list[next_cursor], token_type, values)

	@staticmethod
	def match_(token, token_type, values):
		return token.type == token_type and (values is None or token.value in values)

	@staticmethod
	def expectation_message(expected, got):
		return CompilationEngine.expected_message(expected) + "\n" + CompilationEngine.got_message(got)

	@staticmethod
	def got_message(got):
		return "got      : " + got

	@staticmethod
	def expected_message(expected):
		return "expected : " + expected

	def get_expectation_missmatch(self, token_types, values):
		expected = str("|".join(token_types)) + (" " + str("|".join(values))) if values is not None else ""
		got = str(self.current_token.type.value) + (
				" " + str(self.current_token.value)) if self.current_token.value is not None else ""
		return expected, got

	def error(self, error):
		raise CompilationError(error, self.current_token)

	def keyword(self, values):
		if self.match(Types.Tokens.KEYWORD, values):
			value = self.current_token.value
		else:
			self.error_token_missmatch(Types.Tokens.KEYWORD, values)
		self.advance()
		return value

	def write_token(self):
		with self.xml.tag_scope(str(self.current_token.type.value), True):
			text = str(self.current_token.value)
			text = text.replace("&", "&amp;")
			text = text.replace("<", "&lt;")
			text = text.replace(">", "&gt;")
			self.xml.write(" " + text + " ", False)

	def identifier(self):
		if self.match(Types.Tokens.IDENTIFIER):
			value = self.current_token.value
		else:
			self.error_token_missmatch(Types.Tokens.IDENTIFIER, ["<identifier>"])
		self.advance()
		return value

	def symbol(self, values):
		if self.match(Types.Tokens.SYMBOL, values):
			value = self.current_token.value
		else:
			self.error_token_missmatch(Types.Tokens.SYMBOL, values)
		self.advance()
		return value

	type_keyword_values = ["int", "char", "boolean"]

	def match_type(self):
		return self.match(Types.Tokens.KEYWORD, self.type_keyword_values) or self.match(Types.Tokens.IDENTIFIER)

	def error_token_missmatch(self, token_type, values):
		(expected, got) = self.get_expectation_missmatch([str(token_type.value)], values)
		self.error(self.expectation_message(expected, got))

	def type_(self):
		if self.match_type():
			value = self.current_token.value
		else:
			(expected_keywords, got) = self.get_expectation_missmatch(Types.Tokens.KEYWORD, self.type_keyword_values)
			expected_identifier = self.get_expectation_missmatch(Types.Tokens.IDENTIFIER, ["<class name>"])
			self.error(self.expected_message(expected_keywords) + "\nor\n" + self.expected_message(
				expected_identifier) + "\n" + self.got_message(got))
		self.advance()
		return value

	def parameter_list(self):
		count = 0
		if self.match_type():
			type_ = self.type_()
			name = self.identifier()
			self.symbol_table.define(name, type_, "arg")
			count += 1
			while self.match(Types.Tokens.SYMBOL, ","):
				self.symbol(",")
				type_ = self.type_()
				name = self.identifier()
				self.symbol_table.define(name, type_, "arg")
				count += 1
		return count

	def statements(self):
		while self.match_statement():
			self.statement()

	def match_statement(self):
		return self.match(Types.Tokens.KEYWORD, ["let", "if", "while", "do", "return"])

	def statement(self):
		if self.match(Types.Tokens.KEYWORD, ["let"]):
			self.keyword("let")
			identifier = self.identifier()
			symbol = self.get_symbol(identifier)
			is_array = self.match(Types.Tokens.SYMBOL, "[")
			if is_array:
				self.symbol("[")
				self.expression()
				self.symbol("]")
				self.vm_writer.command_symbol("push", symbol)
				self.vm_writer.command("add")
			self.symbol("=")
			self.expression()
			self.symbol(";")
			if is_array:
				self.vm_writer.command("pop temp 0")
				self.vm_writer.command("pop pointer 1")
				self.vm_writer.command("push temp 0")
				self.vm_writer.command("pop that 0")
			else:
				self.vm_writer.command_symbol("pop", symbol)
		elif self.match(Types.Tokens.KEYWORD, ["if"]):
			self.keyword("if")
			base_label = self.make_label("if")
			if_true = base_label + "_true"
			if_false = base_label + "_false"
			if_end = base_label + "_end"
			self.symbol("(")
			self.expression()
			self.symbol(")")
			self.vm_writer.command("if-goto " + if_true)
			self.vm_writer.command("goto " + if_false)
			self.vm_writer.label(if_true)
			self.symbol("{")
			self.statements()
			self.symbol("}")
			if self.match(Types.Tokens.KEYWORD, ["else"]):
				self.vm_writer.command("goto " + if_end)
				self.vm_writer.label(if_false)
				self.keyword("else")
				self.symbol("{")
				self.statements()
				self.symbol("}")
				self.vm_writer.label(if_end)
			else:
				self.vm_writer.label(if_false)
		elif self.match(Types.Tokens.KEYWORD, ["while"]):
			self.keyword("while")
			base_label = self.make_label("while")
			start_label = base_label + "_start"
			if_end = base_label + "_end"
			self.vm_writer.command("label " + start_label)
			self.symbol("(")
			self.expression()
			self.symbol(")")
			self.vm_writer.command("not")
			self.vm_writer.command("if-goto " + if_end)
			self.symbol("{")
			self.statements()
			self.symbol("}")
			self.vm_writer.command("goto " + start_label)
			self.vm_writer.command("label " + if_end)
		elif self.match(Types.Tokens.KEYWORD, ["do"]):
			self.keyword("do")
			self.subroutine_call()
			self.vm_writer.command("pop temp 0")
			self.symbol(";")
		elif self.match(Types.Tokens.KEYWORD, ["return"]):
			self.keyword("return")
			if self.subroutine_type == "void":
				self.vm_writer.push_constant(0)
			else:
				self.expression()
			self.symbol(";")
			self.vm_writer.command("return")

	def get_symbol(self, symbol_name):
		symbol = self.symbol_table.find(symbol_name)
		if symbol is None:
			self.error("Symbol not found : " + symbol_name)
		return symbol

	def make_label(self, name):
		return self.subroutine_name + "_" + name + "_" + str(self.next_scope_counter(name))

	def next_scope_counter(self, name):
		self.scope_counters[name] = self.scope_counters[name] + 1 if name in self.scope_counters else 0
		return self.scope_counters[name]

	def reset_scope_counter(self):
		self.scope_counters = {}

	def expression(self):
		self.term()
		while self.match(Types.Tokens.SYMBOL, Types.ops.keys()):
			op = self.symbol(Types.ops)
			self.term()
			self.vm_writer.command(Types.ops[op])

	def term(self):
		if self.match_term_constants():
			value = self.current_token.value
			if self.current_token.type == Types.Tokens.INT_CONST:
				self.vm_writer.command("push constant " + value)
			elif self.current_token.type == Types.Tokens.STRING_CONST:
				self.vm_writer.command("push constant " + str(len(value)))
				self.vm_writer.call("String.new", 1)
				for char in value:
					self.vm_writer.command("push constant " + str(ord(char)))
					self.vm_writer.call("String.appendChar", 2)
			elif value in ["null", "false"]:
				self.vm_writer.command("push constant 0")
			elif value == "true":
				self.vm_writer.command("push constant 0")
				self.vm_writer.command("not")
			elif value == "this":
				self.vm_writer.command("push pointer 0")
			else:
				self.error("Invalid constant term")
			self.advance()
		elif self.match(Types.Tokens.IDENTIFIER):
			if self.match_next(Types.Tokens.SYMBOL, ".("):
				self.subroutine_call()
			else:
				symbol = self.identifier()
				if self.match(Types.Tokens.SYMBOL, "["):
					self.symbol("[")
					self.expression()
					self.symbol("]")
					self.vm_writer.command_symbol("push", self.symbol_table.find(symbol))
					self.vm_writer.command("add")
					self.vm_writer.command("pop pointer 1")
					self.vm_writer.command("push that 0")
				else:
					self.vm_writer.command_symbol("push", self.symbol_table.find(symbol))
		elif self.match(Types.Tokens.SYMBOL, "("):
			self.symbol("(")
			self.expression()
			self.symbol(")")
		elif self.match(Types.Tokens.SYMBOL, "-~"):
			symbol = self.symbol(["-", "~"])
			self.term()
			command = "neg" if symbol == "-" else "not"
			self.vm_writer.command(command)
		else:
			self.error("Invalid term : " + str(self.current_token.type.value) + " " + self.current_token.value)

	def subroutine_call(self):
		identifier = self.identifier()
		symbol = self.symbol_table.find(identifier)

		arguments_count = 0
		if symbol is not None:
			self.symbol(".")
			method = self.identifier()
			self.vm_writer.command_symbol("push", symbol)
			arguments_count += 1
			subroutine_to_call = symbol.type + "." + method
		else:
			if self.match(Types.Tokens.SYMBOL, "."):
				self.symbol(".")
				function = self.identifier()
				subroutine_to_call = identifier + "." + function
			else:
				self.vm_writer.command("push pointer 0")
				arguments_count += 1
				subroutine_to_call = self.class_name + "." + identifier

		self.symbol("(")
		arguments_count += self.expression_list()
		self.symbol(")")
		self.vm_writer.call(subroutine_to_call, arguments_count)

	def expression_list(self):
		count = 0
		if self.match_term():
			self.expression()
			count += 1
			while self.match(Types.Tokens.SYMBOL, ","):
				self.symbol(",")
				self.expression()
				count += 1
		return count

	def match_term(self):
		return self.match_term_constants() or self.match(Types.Tokens.IDENTIFIER) or self.match(Types.Tokens.SYMBOL, "(-~")

	def match_term_constants(self):
		return self.match(Types.Tokens.INT_CONST) or self.match(Types.Tokens.STRING_CONST) or self.match(Types.Tokens.KEYWORD, Types.term_keyword_constants)

