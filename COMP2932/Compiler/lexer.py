#!/usr/bin/python3
# By Hollow Man


class Token:
    keywords = ["class", "constructor", "method", "function", "let", "do", "if",
                "int", "boolean", "char", "void", "var", "static", "field",
                "else", "while", "return", "this"]
    # I take "true", "false", "null" as a specific type
    types = ["Identifier", "Integer", "String", "Boolean",
             "Null", "Symbol", "Keyword", "Operator", "Method", "EOF"]
    operators = ["+", "-", "*", "/", "&", "|", "~", "<", ">"]
    symbols = ["{", "}", "[", "]", "(", ")", ",", ";", "=", "."]
    line = 0
    pointer = 0
    code = []

    def __init__(self, code):
        self.code = code

    def GetNextToken(self):
        lexem = ""
        # code is empty or pointer exceeds the line size
        if self.code == []:
            return (None, "EOF")
        while True:
            if self.line >= len(self.code):
                return (None, "EOF")
            if self.pointer >= len(self.code[self.line]):
                self.pointer = 0
                self.line += 1
            else:
                break
        # Consuming beginning tab and whitespace and check then consume comments
        while True:
            while self.code[self.line][self.pointer] == ' ' or self.code[self.line][self.pointer] == '\t':
                self.pointer += 1
                # make sure haven't reached the end of line or file
                while True:
                    if self.line >= len(self.code):
                        return (None, "EOF")
                    if self.pointer >= len(self.code[self.line]):
                        self.pointer = 0
                        self.line += 1
                    else:
                        break
            while self.pointer+1 < len(self.code[self.line]) and self.code[self.line][self.pointer] == '/':
                if self.code[self.line][self.pointer+1] == '/':
                    self.line += 1
                    self.pointer = 0
                    if self.line >= len(self.code):
                        return (None, "EOF")
                elif self.code[self.line][self.pointer+1] == '*':
                    self.pointer += 2
                    # make sure haven't reached the end of line or file
                    while True:
                        if self.pointer+1 < len(self.code[self.line]) and self.code[self.line][self.pointer] == '*':
                            if self.code[self.line][self.pointer+1] == '/':
                                self.pointer += 2
                                break
                        self.pointer += 1
                        # make sure haven't reached the end of line or file
                        while True:
                            if self.line >= len(self.code):
                                raise Exception("Lexical", self.line+1,
                                                "EOF", 'Comments end without */')
                            if self.pointer >= len(self.code[self.line]):
                                self.pointer = 0
                                self.line += 1
                            else:
                                break
                # it's divide symbol
                else:
                    self.pointer += 1
                    return ("/", "Operator")
                # make sure haven't reached the end of line or file
                while True:
                    if self.line >= len(self.code):
                        return (None, "EOF")
                    if self.pointer >= len(self.code[self.line]):
                        self.pointer = 0
                        self.line += 1
                    else:
                        break
            # make sure haven't reached the end of line or file
            while True:
                if self.line >= len(self.code):
                    return (None, "EOF")
                if self.pointer >= len(self.code[self.line]):
                    self.pointer = 0
                    self.line += 1
                else:
                    break
            # To ensure that no remained tab and whitespace and comments
            if not(self.code[self.line][self.pointer] == ' ' or self.code[self.line][self.pointer] == '\t' or self.code[self.line][self.pointer] == '\\'):
                break
        # begin getting a Token
        # String
        if self.pointer < len(self.code[self.line]) and self.code[self.line][self.pointer] == '"':
            self.pointer += 1
            while self.pointer < len(self.code[self.line]):
                if self.code[self.line][self.pointer] == '"':
                    self.pointer += 1
                    if self.pointer >= len(self.code[self.line]):
                        self.pointer = 0
                        self.line += 1
                    return (lexem, "String")
                else:
                    lexem += self.code[self.line][self.pointer]
                    self.pointer += 1
            # Check if the string ends with "
            raise Exception("Lexical", self.line+1,
                            self.code[self.line][self.pointer-1], 'a string ended without "')
        # Others
        while self.pointer < len(self.code[self.line]) and self.code[self.line][self.pointer] != ' ':
            # raise error if there exists special symbols
            if not (self.code[self.line][self.pointer].isalnum() or self.code[self.line][self.pointer] == '_' or self.code[self.line][self.pointer] in self.operators or self.code[self.line][self.pointer] in self.symbols):
                raise Exception("Lexical", self.line+1,
                                self.code[self.line][self.pointer], 'unrecognised symbol')
            lexem += self.code[self.line][self.pointer]
            # To identify symbols
            if self.code[self.line][self.pointer] in self.operators:
                self.pointer += 1
                return (lexem, "Operator")
            elif self.code[self.line][self.pointer] in self.symbols:
                self.pointer += 1
                return (lexem, "Symbol")
            # To cut symbols with words
            elif self.pointer+1 < len(self.code[self.line]) and not (self.code[self.line][self.pointer+1].isalnum() or self.code[self.line][self.pointer+1] == '_'):
                self.pointer += 1
                break
            self.pointer += 1
        # Reconize the type of lexem
        if lexem in self.keywords:
            return (lexem, "Keyword")
        elif lexem == "true" or lexem == "false":
            return (lexem, "Boolean")
        elif lexem == "null":
            return (lexem, "Null")
        elif lexem.isnumeric():
            return (int(lexem), "Integer")
        elif lexem[0].isalpha() or lexem[0] == "_":
            return (lexem, "Identifier")
        # Error when don't match any type of lexem
        else:
            raise Exception("Lexical", self.line+1,
                            self.code[self.line][self.pointer-1], 'wrong identifier')

    def PeekNextToken(self):
        oldline = self.line
        oldpointer = self.pointer
        token = self.GetNextToken()
        self.line = oldline
        self.pointer = oldpointer
        return token
