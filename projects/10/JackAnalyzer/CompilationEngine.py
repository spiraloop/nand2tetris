import Types


class Xml:
    def __init__(self, file):
        self.file = file
        self.level = 0

    def tag_scope(self, tag, inline=False):
        return TagScope(self, tag, inline)

    def write(self, text, indent=True):
        if indent:
            self.file.write(self.level * "  ")
        self.file.write(text)


class TagScope:
    def __init__(self, xml, tag, inline):
        self.xml = xml
        self.tag = tag
        self.inline = inline

    def __enter__(self):
        self.xml.write("<" + self.tag + ">" + ("\n" if not self.inline else ""))
        if not self.inline:
            self.xml.level += 1

    def __exit__(self, exc_type, exc_val, traceback):
        if not self.inline:
            self.xml.level -= 1
        self.xml.write("</" + self.tag + ">\n", not self.inline)


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
        self.xml = Xml(output_file)

    def compile(self):
        self.class_()
        pass

    def advance(self):
        self.token_cursor += 1
        if self.token_cursor > self.token_list_size:
            self.error("Unexpected end of file")

        if self.token_cursor < self.token_list_size:
            self.current_token = self.token_list[self.token_cursor]

    def class_(self):
        with self.xml.tag_scope("class"):
            self.keyword("class")

            self.identifier()

            self.symbol('{')

            self.class_variables()
            self.class_subroutines()

            self.symbol('}')

    def class_variables(self):
        declaration_type = ["static", "field"]
        while self.match(Types.Tokens.KEYWORD, declaration_type):
            with self.xml.tag_scope("classVarDec"):
                self.keyword(declaration_type)
                self.variable_list()
                self.symbol(";")

    def variable_list(self):
        self.type_()
        self.identifier()
        while self.match(Types.Tokens.SYMBOL, [","]):
            self.symbol(",")
            self.identifier()

    routine_types = ["constructor", "function", "method"]

    def class_subroutines(self):
        while self.match(Types.Tokens.KEYWORD, self.routine_types):
            self.subroutine()

    def subroutine(self):
        with self.xml.tag_scope("subroutineDec"):
            self.keyword(self.routine_types)

            if self.match(Types.Tokens.KEYWORD, ["void"]):
                self.keyword("void")
            else:
                self.type_()

            self.identifier()

            self.symbol("(")
            self.parameter_list()
            self.symbol(")")

            with self.xml.tag_scope("subroutineBody"):
                self.symbol("{")
                self.subroutine_variables()
                self.statements()
                self.symbol("}")

    def subroutine_variables(self):
        while self.match(Types.Tokens.KEYWORD, ["var"]):
            with self.xml.tag_scope("varDec"):
                self.keyword("var")
                self.variable_list()
                self.symbol(";")

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
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.KEYWORD, values)
        self.advance()

    def write_token(self):
        with self.xml.tag_scope(str(self.current_token.type.value), True):
            text = str(self.current_token.value)
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            self.xml.write(" " + text + " ", False)

    def identifier(self):
        if self.match(Types.Tokens.IDENTIFIER):
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.IDENTIFIER, ["<identifier>"])
        self.advance()

    def symbol(self, values):
        if self.match(Types.Tokens.SYMBOL, values):
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.SYMBOL, values)
        self.advance()

    type_keyword_values = ["int", "char", "boolean"]

    def match_type(self):
        return self.match(Types.Tokens.KEYWORD, self.type_keyword_values) or self.match(Types.Tokens.IDENTIFIER)

    def error_token_missmatch(self, token_type, values):
        (expected, got) = self.get_expectation_missmatch([str(token_type.value)], values)
        self.error(self.expectation_message(expected, got))

    def type_(self):
        if self.match_type():
            self.write_token()
        else:
            (expected_keywords, got) = self.get_expectation_missmatch(Types.Tokens.KEYWORD, self.type_keyword_values)
            expected_identifier = self.get_expectation_missmatch(Types.Tokens.IDENTIFIER, ["<class name>"])
            self.error(self.expected_message(expected_keywords) + "\nor\n" + self.expected_message(
                expected_identifier) + "\n" + self.got_message(got))
        self.advance()

    def parameter_list(self):
        with self.xml.tag_scope("parameterList"):
            if self.match_type():
                self.type_()
                self.identifier()
                while self.match(Types.Tokens.SYMBOL, ","):
                    self.symbol(",")
                    self.type_()
                    self.identifier()

    def statements(self):
        with self.xml.tag_scope("statements"):
            while self.match_statement():
                self.statement()

    def match_statement(self):
        return self.match(Types.Tokens.KEYWORD, ["let", "if", "while", "do", "return"])

    def statement(self):
        if self.match(Types.Tokens.KEYWORD, ["let"]):
            with self.xml.tag_scope("letStatement"):
                self.keyword("let")
                self.identifier()
                if self.match(Types.Tokens.SYMBOL, "["):
                    self.symbol("[")
                    self.expression()
                    self.symbol("]")
                self.symbol("=")
                self.expression()
                self.symbol(";")
        elif self.match(Types.Tokens.KEYWORD, ["if"]):
            with self.xml.tag_scope("ifStatement"):
                self.keyword("if")
                self.symbol("(")
                self.expression()
                self.symbol(")")
                self.symbol("{")
                self.statements()
                self.symbol("}")
                if self.match(Types.Tokens.KEYWORD, ["else"]):
                    self.keyword("else")
                    self.symbol("{")
                    self.statements()
                    self.symbol("}")
        elif self.match(Types.Tokens.KEYWORD, ["while"]):
            with self.xml.tag_scope("whileStatement"):
                self.keyword("while")
                self.symbol("(")
                self.expression()
                self.symbol(")")
                self.symbol("{")
                self.statements()
                self.symbol("}")
        elif self.match(Types.Tokens.KEYWORD, ["do"]):
            with self.xml.tag_scope("doStatement"):
                self.keyword("do")
                self.subroutine_call()
                self.symbol(";")
        elif self.match(Types.Tokens.KEYWORD, ["return"]):
            with self.xml.tag_scope("returnStatement"):
                self.keyword("return")
                if self.match_term():
                    self.expression()
                self.symbol(";")

    def expression(self):
        with self.xml.tag_scope("expression"):
            self.term()
            ops = "+-*/&|<>="
            while self.match(Types.Tokens.SYMBOL, ops):
                self.symbol(ops)
                self.term()

    def term(self):
        with self.xml.tag_scope("term"):
            if self.match_term_constants():
                self.write_token()
                self.advance()
            elif self.match(Types.Tokens.IDENTIFIER):
                if self.match_next(Types.Tokens.SYMBOL, ".("):
                    self.subroutine_call()
                else:
                    self.identifier()
                    if self.match(Types.Tokens.SYMBOL, "["):
                        self.symbol("[")
                        self.expression()
                        self.symbol("]")
            elif self.match(Types.Tokens.SYMBOL, "("):
                self.symbol("(")
                self.expression()
                self.symbol(")")
            elif self.match(Types.Tokens.SYMBOL, "-~"):
                self.symbol(["-", "~"])
                self.term()
            else:
                self.error("Invalid term : " + str(self.current_token.type.value) + " " + self.current_token.value)

    def subroutine_call(self):
        self.identifier()
        if self.match(Types.Tokens.SYMBOL, "."):
            self.symbol(".")
            self.identifier()
        self.symbol("(")
        self.expression_list()
        self.symbol(")")

    def expression_list(self):
        with self.xml.tag_scope("expressionList"):
            if self.match_term():
                self.expression()
                while self.match(Types.Tokens.SYMBOL, ","):
                    self.symbol(",")
                    self.expression()

    def match_term(self):
        return self.match_term_constants() or self.match(Types.Tokens.IDENTIFIER) or self.match(Types.Tokens.SYMBOL, "(-~")

    def match_term_constants(self):
        return self.match(Types.Tokens.INT_CONST) or self.match(Types.Tokens.STRING_CONST) or self.match(Types.Tokens.KEYWORD, self.keyword_constants)

    keyword_constants = ["true", "false", "null", "this"]
