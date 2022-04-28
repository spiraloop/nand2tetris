import Types


class Symbol:
	def __init__(self, name, type_, kind, index):
		self.name = name
		self.type = type_
		self.kind = kind
		self.index = index


class SymbolTable:
	def __init__(self):
		self.class_scopes = {}
		self.subroutine_scopes = {}

	def define(self, name, type_, kind):
		self.scope(kind)[name] = Symbol(name, type_, kind, self.var_count(kind))

	def scope(self, kind):
		return self.class_scopes if kind in ["field", "static"] else self.subroutine_scopes

	def start_subroutine(self):
		self.subroutine_scopes = {}

	def find(self, symbol_name):
		symbol = None
		if symbol_name in self.subroutine_scopes:
			symbol = self.subroutine_scopes[symbol_name]
		elif symbol_name in self.class_scopes:
			symbol = self.class_scopes[symbol_name]
		return symbol

	def var_count(self, kind):
		return sum(1 for symbol in self.scope(kind).values() if symbol.kind == kind)

