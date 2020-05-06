#!/usr/bin/python3
# By Hollow Man

class SymbolTable:
    table = {}
    level = []

    def Add(self, name, dtype, kind, assign, new, firstt,offset=0):
        result = self.Find(name)
        if new:
            if result:
                if firstt:
                    return False
        symbol = {}
        info = []
        info.append(dtype)
        info.append(kind)
        info.append(assign)
        if not new:
            if len(result) == 2:
                info.append(result[0][-1])
                symbol = self.table[str(self.level[:-result[1]])]
                symbol[name] = info[:]
                self.table[str(self.level[:-result[1]])] = symbol
                return True
            else:
                info.append(result[-1])
        else:
            info.append(offset)
        if str(self.level) in self.table:
            symbol = self.table[str(self.level)]
        symbol[name] = info[:]
        self.table[str(self.level)] = symbol
        return True

    def Find(self, name, deep=True):
        if str(self.level) in self.table:
            if name in self.table[str(self.level)]:
                return self.table[str(self.level)][name]
        if deep:
            loop = 1
            while loop < len(self.level):
                if str(self.level[:-loop]) in self.table:
                    if name in self.table[str(self.level[:-loop])]:
                        return self.table[str(self.level[:-loop])][name], loop
                loop += 1
            return False

global symboltable
symboltable = SymbolTable()
ifnum=0
whilenum=0

def start(token, table):
    global symboltable
    symboltable.table = table
    symboltable.level = []
    count = 0
    while True:
        nextToken = token.PeekNextToken()
        if nextToken[0] == "class":
            classDeclar(token,count)
            count += 1
        elif nextToken[1] == "EOF":
            break
        else:
            # Check whether there is code outside the class block
            raise Exception('Semantic', token.line+1,
                            token.code[token.line][token.pointer-1], "unreachable code outside the class block")
    return symboltable.table


def classDeclar(token, count):
    nextToken = token.GetNextToken()
    if nextToken[0] == "class":
        nextToken = token.GetNextToken()
        if nextToken[1] == "Identifier":
            symboltable.level.append(nextToken[0])
            if not symboltable.Add(nextToken[0], nextToken[0], "class", False, True,True, count):
                raise Exception(
                    'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+"class has declared")
            nextToken = token.GetNextToken()
            if nextToken[0] == "{":
                nextToken = token.PeekNextToken()
                counts = 0
                countf = 0
                while True:
                    if nextToken[0] == 'static':
                        classVarDeclar(token, counts)
                        counts += 1
                    elif nextToken[0] == 'field':
                        classVarDeclar(token, countf)
                        countf += 1
                    else:
                        break
                    nextToken = token.PeekNextToken()
                countc = 0
                countf = 0
                countm = 0
                while True:
                    if nextToken[0] == 'constructor':
                        countc = subroutineDeclar(token, countc)
                        countc += 1
                    elif nextToken[0] == 'function':
                        countf = subroutineDeclar(token, countf)
                        countf += 1
                    elif nextToken[0] == 'method':
                        countm = subroutineDeclar(token, countm)
                        countm += 1
                    else:
                        break
                    nextToken = token.PeekNextToken()
                nextToken = token.GetNextToken()
                if nextToken[0] == "}":
                    del symboltable.level[-1]
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'}' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'{' expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'class' expected at this area")


def classVarDeclar(token, count):
    nextToken = token.GetNextToken()
    if nextToken[0] == 'static' or nextToken[0] == 'field':
        kind = nextToken[0]
        nextToken = token.GetNextToken()
        if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
            type = nextToken[0]
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                if not symboltable.Add(nextToken[0], type, kind, False, True,True, count):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared in this class")
                nextToken = token.GetNextToken()
                while nextToken[0] == ',':
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        count += 1
                        if not symboltable.Add(nextToken[0], type, kind, False, True,True, count):
                            raise Exception(
                                'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared in this class")
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
                    nextToken = token.GetNextToken()
                if nextToken[0] == ";":
                    return count
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "';' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a type at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'static' or 'field' expected at this area")


def subroutineDeclar(token, count):
    nextToken = token.GetNextToken()
    if nextToken[0] == 'constructor' or nextToken[0] == 'function' or nextToken[0] == 'method':
        kind = nextToken[0]
        nextToken = token.GetNextToken()
        if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
            type = nextToken[0]
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                if not symboltable.Add(nextToken[0], type, kind, False, True,True, count):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared in this class")
                symboltable.level.append(nextToken[0])
                nextToken = token.GetNextToken()
                if nextToken[0] == "(":
                    paramList(token)
                    nextToken = token.GetNextToken()
                    if nextToken[0] == ")":
                        nextToken = token.GetNextToken()
                        if nextToken[0] == "{":
                            while statementTest(token):
                                statement(token)
                            nextToken = token.GetNextToken()
                            if nextToken[0] == "}":
                                del symboltable.level[-1]
                                return count
                            else:
                                raise Exception(
                                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'}' expected at this area")
                        else:
                            raise Exception(
                                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'{' expected at this area")
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'(' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a type at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'static' or 'field' expected at this area")

# using to test whether it's possibly a statement by checking it's head


def statementTest(token):
    nextToken = token.PeekNextToken()
    if nextToken[0] == 'if' or nextToken[0] == 'var' or nextToken[0] == 'let' or nextToken[0] == 'while' or nextToken[0] == 'do' or nextToken[0] == 'return':
        return True
    else:
        return False


def statement(token):
    nextToken = token.PeekNextToken()
    if nextToken[0] == 'if':
        ifStatement(token)
    elif nextToken[0] == 'var':
        varDeclarStatement(token)
    elif nextToken[0] == 'let':
        letStatement(token)
    elif nextToken[0] == 'while':
        whileStatement(token)
    elif nextToken[0] == 'do':
        doStatement(token)
    elif nextToken[0] == 'return':
        returnStatement(token)
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a statement at this area")


def paramList(token):
    nextToken = token.PeekNextToken()
    if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
        type = nextToken[0]
        nextToken = token.GetNextToken()
        nextToken = token.GetNextToken()
        count = 0
        if nextToken[1] == "Identifier":
            symboltable.Add(nextToken[0], type, "argument",False,True,True, count)
            count += 1
            nextToken = token.PeekNextToken()
            while nextToken[0] == ',':
                nextToken = token.GetNextToken()
                nextToken = token.GetNextToken()
                if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
                    type = nextToken[0]
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        symboltable.Add(nextToken[0], type, "argument",False,True,True, count)
                        count += 1
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a type at this area")
                nextToken = token.PeekNextToken()
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")


def varDeclarStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "var":
        kind = nextToken[0]
        nextToken = token.GetNextToken()
        if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
            type = nextToken[0]
            nextToken = token.GetNextToken()
            numLocalVariables = 0
            if nextToken[1] == "Identifier":
                if not symboltable.Add(nextToken[0], type, kind, False, True,True, numLocalVariables):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared")
                numLocalVariables += 1
                nextToken = token.GetNextToken()
                while nextToken[0] == ',':
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        if not symboltable.Add(nextToken[0], type, kind, False, True,True, numLocalVariables):
                            raise Exception(
                                'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared")
                        numLocalVariables += 1
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
                    nextToken = token.GetNextToken()
                if nextToken[0] == ";":
                    pass
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "';' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a type at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'var' expected at this area")


def letStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "let":
        nextToken = token.GetNextToken()
        if nextToken[1] == "Identifier":
            res=symboltable.Find(nextToken[0])
            if not res:
                raise Exception('Semantic', token.line+1,
                        token.code[token.line][token.pointer-1], nextToken[0]+" hasn't declared")
            else:
                if len(res) == 2:
                    if res[0][2]:
                        pass
                    else:
                        symboltable.Add(nextToken[0], res[0][0], res[0][1], True, False, True)
                else:
                    if res[2]:
                        pass
                    else:
                        symboltable.Add(nextToken[0], res[0], res[1], True, False, True)
                    ftype = res[0]
            nextToken = token.PeekNextToken()
            if nextToken[0] == "[":
                nextToken = token.GetNextToken()
                expression(token)
                nextToken = token.GetNextToken()
                if nextToken[0] == "]":
                    nextToken = token.PeekNextToken()
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "']' expected at this area")
            if nextToken[0] == "=":
                nextToken = token.GetNextToken()
                expression(token)
                nextToken = token.GetNextToken()
                if nextToken[0] == ";":
                    pass
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "';' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'=' expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'let' expected at this area")


def ifStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "if":
        nextToken = token.GetNextToken()
        if nextToken[0] == "(":
            expression(token)
            nextToken = token.GetNextToken()
            if nextToken[0] == ")":
                global ifnum
                symboltable.level.append("if"+str(ifnum))
                ifnum+=1
                nextToken = token.GetNextToken()
                if nextToken[0] == "{":
                    while statementTest(token):
                        statement(token)
                    nextToken = token.GetNextToken()
                    if nextToken[0] == "}":
                        nextToken = token.PeekNextToken()
                        if nextToken[0] == "else":
                            nextToken = token.GetNextToken()
                            nextToken = token.GetNextToken()
                            if nextToken[0] == "{":
                                while statementTest(token):
                                    statement(token)
                                nextToken = token.GetNextToken()
                                if nextToken[0] == "}":
                                    pass
                                else:
                                    raise Exception(
                                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'}' expected at this area")
                            else:
                                raise Exception(
                                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'{' expected at this area")
                        del symboltable.level[-1]
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'}' expected at this area")
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'{' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'(' expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'if' expected at this area")


def whileStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "while":
        nextToken = token.GetNextToken()
        if nextToken[0] == "(":
            expression(token)
            nextToken = token.GetNextToken()
            if nextToken[0] == ")":
                global whilenum
                symboltable.level.append("while"+str(whilenum))
                whilenum+=1
                nextToken = token.GetNextToken()
                if nextToken[0] == "{":
                    while statementTest(token):
                        statement(token)
                    nextToken = token.GetNextToken()
                    if nextToken[0] == "}":
                        del symboltable.level[-1]
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'}' expected at this area")
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'{' expected at this area")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'(' expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'while' expected at this area")


def doStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "do":
        subroutineCall(token)
        nextToken = token.GetNextToken()
        if nextToken[0] == ";":
            pass
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "';' expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'do' expected at this area")


def subroutineCall(token):
    nextToken = token.GetNextToken()
    if nextToken[1] == "Identifier":
        nextToken = token.GetNextToken()
        if nextToken[0] == ".":
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier" or nextToken[1] == "Method":
                nextToken = token.GetNextToken()
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
        if nextToken[0] == "(":
            expressionList(token)
            nextToken = token.GetNextToken()
            if nextToken[0] == ")":
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'(' expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "an identifier expected at this area")


def expressionList(token):
    if factorTest(token):
        expression(token)
        while True:
            nextToken = token.PeekNextToken()
            if nextToken[0] == ",":
                nextToken = token.GetNextToken()
                expression(token)
            else:
                break


def returnStatement(token):
    nextToken = token.GetNextToken()
    if nextToken[0] == "return":
        if factorTest(token):
            expression(token)
        nextToken = token.GetNextToken()
        if nextToken[0] == ";":
            pass
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'return' expected at this area")
        nextToken = token.PeekNextToken()
        if nextToken[0] == "}" or nextToken[0] == "else":
            pass
        else:
            raise Exception('Semantic', token.line+1,
                            token.code[token.line][token.pointer-1], "unreachable code after return statement")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "'return' expected at this area")


def expression(token):
    if factorTest(token):
        relationalExpression(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '&' or nextToken[0] == '|':
            nextToken = token.GetNextToken()
            relationalExpression(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a relational expression at this area")


def relationalExpression(token):
    if factorTest(token):
        arithmeticExpression(token)
        nextToken = token.PeekNextToken()
        while True:
            # I think the provided full jack grammar make a mistake here, so I correct it.
            if nextToken[0] == "=":
                nextToken = token.GetNextToken()
                arithmeticExpression(token)
                nextToken = token.PeekNextToken()
            elif nextToken[0] == '>' or nextToken[0] == '<':
                nextToken = token.GetNextToken()
                nextToken = token.PeekNextToken()
                if nextToken[0] == "=":
                    nextToken = token.GetNextToken()
                arithmeticExpression(token)
                nextToken = token.PeekNextToken()
            else:
                break
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a arithmetic expression at this area")


def arithmeticExpression(token):
    if factorTest(token):
        term(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '+' or nextToken[0] == '-':
            nextToken = token.GetNextToken()
            term(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a term at this area")


def term(token):
    if factorTest(token):
        factor(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '*' or nextToken[0] == '/':
            nextToken = token.GetNextToken()
            factor(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a factor at this area")


def factor(token):
    nextToken = token.PeekNextToken()
    if nextToken[0] == '-' or nextToken[0] == '~':
        nextToken = token.GetNextToken()
    nextToken = token.GetNextToken()
    if nextToken[1] == 'Integer' or nextToken[1] == 'String' or nextToken[0] == 'true' or nextToken[0] == 'false' or nextToken[0] == 'null' or nextToken[0] == 'this':
        pass
    elif nextToken[1] == 'Identifier':
        nextToken = token.PeekNextToken()
        if nextToken[0] == '.':
            nextToken = token.GetNextToken()
            nextToken = token.GetNextToken()
            if nextToken[1] == 'Identifier':
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a identifier at this area")
            nextToken = token.PeekNextToken()
        if nextToken[0] == '[':
            nextToken = token.GetNextToken()
            expression(token)
            nextToken = token.GetNextToken()
            if nextToken[0] == ']':
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "']' expected at this area")
        if nextToken[0] == '(':
            nextToken = token.GetNextToken()
            expressionList(token)
            nextToken = token.GetNextToken()
            if nextToken[0] == ')':
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
    elif nextToken[0] == '(':
        expressionList(token)
        nextToken = token.GetNextToken()
        if nextToken[0] == ')':
            pass
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")

# using to test whether it's possibly an expression by checking it's head


def factorTest(token):
    nextToken = token.PeekNextToken()
    if nextToken[1] == 'Integer' or nextToken[0] == '-' or nextToken[0] == '~' or nextToken[1] == 'String' or nextToken[0] == 'true' or nextToken[0] == 'false' or nextToken[0] == 'null' or nextToken[0] == 'this' or nextToken[1] == 'Identifier' or nextToken[0] == '(':
        return True
    else:
        return False
