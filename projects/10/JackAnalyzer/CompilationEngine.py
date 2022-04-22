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


class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.xml = Xml(output_file)

    def compile(self):
        self.class_()
        pass

    def advance(self):
        self.tokenizer.advance()

    def class_(self):
        with self.xml.tag_scope("class") as tag:
            self.keyword("class")

            self.identifier()

            self.symbol('{')

            self.class_variables()
            self.class_subroutines()

            self.symbol('}')

    def class_variables(self):
        declaration_type = ["static", "field"]
        while self.match(Types.Tokens.KEYWORD, declaration_type):
            with self.xml.tag_scope("classVarDec") as tag:
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
        with self.xml.tag_scope("subroutineDec") as subroutineDec:
            self.keyword(self.routine_types)

            if self.match(Types.Tokens.KEYWORD, ["void"]):
                self.keyword("void")
            else:
                self.type_()

            self.identifier()

            self.symbol("(")
            self.parameter_list()
            self.symbol(")")

            with self.xml.tag_scope("subroutineBody") as subroutineBody:
                self.symbol("{")
                self.subroutine_variables()
                self.statements()
                self.symbol("}")

    def subroutine_variables(self):
        while self.match(Types.Tokens.KEYWORD, "var"):
            with self.xml.tag_scope("varDec") as varDec:
                self.keyword("var")
                self.variable_list()
                self.symbol(";")

    def match(self, token_type, values):
        return self.match_token(token_type) and self.match_value(values)

    def match_token(self, token_type):
        return self.tokenizer.type == token_type

    def match_value(self, values):
        return self.tokenizer.value in values

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
        got = str(self.tokenizer.type.value) + (
                " " + str(self.tokenizer.value)) if self.tokenizer.value is not None else ""
        return expected, got

    def error(self, error):
        self.tokenizer.error("Compilation error\n" + error)

    def keyword(self, values):
        if self.match_token(Types.Tokens.KEYWORD) and self.match_value(values):
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.KEYWORD, values)
        self.advance()

    def write_token(self):
        with self.xml.tag_scope(str(self.tokenizer.type.value), True) as token:
            self.xml.write(" " + str(self.tokenizer.value) + " ", False)

    def identifier(self):
        if self.match_identifier():
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.IDENTIFIER, ["<identifier>"])
        self.advance()

    def symbol(self, values):
        if self.match_token(Types.Tokens.SYMBOL) and self.match_value(values):
            self.write_token()
        else:
            self.error_token_missmatch(Types.Tokens.SYMBOL, values)
        self.advance()

    type_keyword_values = ["int", "char", "boolean"]

    def match_type(self):
        return self.match(Types.Tokens.KEYWORD, self.type_keyword_values) or self.match_token(Types.Tokens.IDENTIFIER)

    def error_token_missmatch(self, token_type, values):
        (expected, got) = self.get_expectation_missmatch([str(token_type)], values)
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
        with self.xml.tag_scope("parameterList") as tag:
            if self.match_type():
                self.type_()
                self.identifier()
                while self.match(Types.Tokens.SYMBOL, ","):
                    self.symbol(",")
                    self.type_()
                    self.identifier()

    def statements(self):
        with self.xml.tag_scope("statements") as statements:
            while self.match_statement():
                self.statement()

    def match_statement(self):
        return self.match(Types.Tokens.KEYWORD, ["let", "if", "while", "do", "return"])

    def statement(self):
        if self.match(Types.Tokens.KEYWORD, ["let"]):
            with self.xml.tag_scope("letStatement") as letStatement:
                self.keyword("let")
                self.identifier()
                self.symbol("=")
                self.expression()
                self.symbol(";")
        elif self.match(Types.Tokens.KEYWORD, ["if"]):
            with self.xml.tag_scope("ifStatement") as ifStatement:
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
            with self.xml.tag_scope("whileStatement") as whileStatement:
                self.keyword("while")
                self.symbol("(")
                self.expression()
                self.symbol(")")
                self.symbol("{")
                self.statements()
                self.symbol("}")
        elif self.match(Types.Tokens.KEYWORD, ["do"]):
            with self.xml.tag_scope("doStatement") as doStatement:
                self.keyword("do")
                self.subroutine_call()
                self.symbol(";")
        elif self.match(Types.Tokens.KEYWORD, ["return"]):
            with self.xml.tag_scope("returnStatement") as returnStatement:
                self.keyword("return")
                if self.match_token(Types.Tokens.IDENTIFIER):
                    self.expression()
                self.symbol(";")

    def expression(self):
        with self.xml.tag_scope("expression") as expression:
            self.term()

    def term(self):
        with self.xml.tag_scope("term") as term:
            self.identifier()

    def subroutine_call(self):
        self.identifier()
        if self.match(Types.Tokens.SYMBOL, "."):
            self.symbol(".")
            self.identifier()
        self.symbol("(")
        self.expression_list()
        self.symbol(")")

    def expression_list(self):
        with self.xml.tag_scope("expressionList") as expressionList:
            if self.match_identifier():
                self.expression()
                while self.match(Types.Tokens.SYMBOL, ","):
                    self.symbol(",")
                    self.expression()

    def match_identifier(self):
        return self.match_token(Types.Tokens.IDENTIFIER) or self.match(Types.Tokens.KEYWORD, ["this"])
