#!/usr/bin/python3
# By Hollow Man

import SymbolTable

global symboltable, tempexp
generatedcode = ""
symboltable = SymbolTable.SymbolTable()
labelNum = 0
numExpressions = 0
fieldCount = 0
tempexp = ""
tempclassN = ""
subName = ""
isSubroutineBody = False
isConstructor = False
isMethod = False
VM_OPERATORS = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2',
                '/': 'call Math.divide 2', '|': 'or', '&': 'and', '<': 'lt', '>': 'gt', '=': 'eq', }
UNARY_OPERATORS = {'~': 'not', '-': 'neg'}

# Code Generation


def writePush(segment, index):
    global generatedcode
    # possible segments: const, arg, local, static, this, that, pointer, temp
    generatedcode += "push " + segment + " " + str(index)+"\n"


def writePop(segment, index):
    global generatedcode
    generatedcode += "pop " + segment + " " + str(index)+"\n"


def writeArithmetic(command):
    global generatedcode
    # possible commands: add, sub, neg, eq, gt, lt, and, or, not
    generatedcode += command+"\n"


def writeLabel(label):
    global generatedcode
    generatedcode += "label " + label+"\n"


def writeGoto(label):
    global generatedcode
    generatedcode += "goto " + label+"\n"


def writeIf(label):
    global generatedcode
    generatedcode += "if-goto " + label+"\n"


def writeCall(name, nArgs):
    global generatedcode
    generatedcode += "call " + name + " " + str(nArgs)+"\n"


def writeFunction(name, nLocals):
    global generatedcode
    generatedcode += "function " + name + " " + str(nLocals)+"\n"


def writeReturn():
    global generatedcode
    generatedcode += "push constant 0\nreturn\n"

# Parser


def start(token, table, system=False):
    global symboltable, generatedcode
    symboltable.table = table
    symboltable.level = []
    generatedcode = ""
    count = 0
    while True:

        nextToken = token.PeekNextToken()
        if nextToken[0] == "class":
            classDeclar(token, count)
            count += 1
        elif nextToken[1] == "EOF":
            break
        else:
            # Check whether there is code outside the class block
            raise Exception('Semantic', token.line+1,
                            token.code[token.line][token.pointer-1], "unreachable code outside the class block")
    if system:
        return symboltable.table
    else:
        return generatedcode, symboltable.table


def classDeclar(token, count):
    nextToken = token.GetNextToken()
    if nextToken[0] == "class":
        nextToken = token.GetNextToken()
        if nextToken[1] == "Identifier":
            global tempclassN
            tempclassN = nextToken[0]
            if not symboltable.Add(nextToken[0], nextToken[0], "class", False, True, False, count):
                raise Exception(
                    'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" class has declared")
            symboltable.level.append(nextToken[0])
            symboltable.Add(nextToken[0], nextToken[0],
                            "class", False, True, False, count)
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
        if nextToken[0] == 'field':
            global fieldCount
            fieldCount += 1
        nextToken = token.GetNextToken()
        if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
            type = nextToken[0]
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                if not symboltable.Add(nextToken[0], type, kind, False, True, False, count):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared in this class")
                nextToken = token.GetNextToken()
                while nextToken[0] == ',':
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        count += 1
                        if not symboltable.Add(nextToken[0], type, kind, False, True, False, count):
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
    global generatedcode
    nextToken = token.GetNextToken()
    if nextToken[0] == 'constructor' or nextToken[0] == 'function' or nextToken[0] == 'method':
        kind = nextToken[0]
        global isSubroutineBody, isConstructor, isMethod
        isSubroutineBody = True
        if nextToken[0] == 'constructor':
            isConstructor = True
        elif nextToken[0] == 'method':
            isMethod = True
        generatedcode += kind+" "
        nextToken = token.GetNextToken()
        if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
            type = nextToken[0]
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                global subName
                subName = nextToken[0]
                if not symboltable.Add(nextToken[0], type, kind, False, True, False, count):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared in this class")
                symboltable.level.append(nextToken[0])
                symboltable.Add(nextToken[0], type,
                                kind, False, True, False, count)
                generatedcode += nextToken[0]+" "+str(count)+"\n"
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
                                isSubroutineBody = False
                                isConstructor = False
                                isMethod = False
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
            if not symboltable.Add(nextToken[0], type, "argument", False, True, False, count):
                raise Exception(
                    'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+", fobid using the same parameter")
            count += 1
            nextToken = token.PeekNextToken()
            while nextToken[0] == ',':
                nextToken = token.GetNextToken()
                nextToken = token.GetNextToken()
                if nextToken[0] == "void" or nextToken[0] == "int" or nextToken[0] == "char" or nextToken[0] == "boolean" or nextToken[1] == "Identifier":
                    type = nextToken[0]
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        if not symboltable.Add(nextToken[0], type, "argument", False, True, False, count):
                            raise Exception(
                                'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+"fobid using the same parameter")
                        count += 1
                        global numExpressions
                        numExpressions += count
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
                if not symboltable.Add(nextToken[0], type, kind, False, True, False, numLocalVariables):
                    raise Exception(
                        'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared")
                numLocalVariables += 1
                nextToken = token.GetNextToken()
                while nextToken[0] == ',':
                    nextToken = token.GetNextToken()
                    if nextToken[1] == "Identifier":
                        if not symboltable.Add(nextToken[0], type, kind, False, True, False, numLocalVariables):
                            raise Exception(
                                'Semantic', token.line+1, token.code[token.line][token.pointer-1], nextToken[0]+" has declared")
                        numLocalVariables += 1
                    else:
                        raise Exception(
                            'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
                    nextToken = token.GetNextToken()
                if nextToken[0] == ";":
                    if isSubroutineBody:
                        global tempclassN, subName, fieldCount
                        writeFunction(tempclassN + '.' +
                                      subName, numLocalVariables)
                        if isConstructor:
                            writePush("constant", fieldCount)
                            # allocate space for this object
                            writeCall("Memory.alloc", 1)
                            writePop("pointer", 0)  # assign object to 'this'
                        elif isMethod:
                            writePush("argument", 0)
                            writePop("pointer", 0)
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
    global generatedcode,tempexp
    nextToken = token.GetNextToken()
    if nextToken[0] == "let":
        nextToken = token.GetNextToken()
        if nextToken[1] == "Identifier":
            ftype = ""
            fkind = ""
            identi = nextToken[0]
            templev = []
            res = symboltable.Find(nextToken[0])
            if not res:
                raise Exception('Semantic', token.line+1,
                                token.code[token.line][token.pointer-1], nextToken[0]+" hasn't declared")
            else:
                if len(res) == 2:
                    if res[0][2]:
                        pass
                    else:
                        symboltable.Add(
                            nextToken[0], res[0][0], res[0][1], True, False, False)
                    ftype = res[0][0]
                    fkind = res[0][1]
                else:
                    if res[2]:
                        pass
                    else:
                        symboltable.Add(
                            nextToken[0], res[0], res[1], True, False, False)
                    ftype = res[0]
            nextToken = token.PeekNextToken()
            containsList = False
            if nextToken[0] == "[":
                nextToken = token.GetNextToken()
                expression(token)
                nextToken = token.GetNextToken()
                containsList = True
                if len(res) == 2:
                    writePush(res[0][1], res[0][3])
                else:
                    writePush(res[1], res[3])
                writeArithmetic('add')
                mark = False
                if nextToken[0] == "]":
                    if str(symboltable.level) in symboltable.table:
                        if identi in symboltable.table[str(symboltable.level)]:
                            templev = symboltable.level[:]
                            mark = True
                    if not mark:
                        loop = 1
                        while loop < len(symboltable.level):
                            if str(symboltable.level[:-loop]) in symboltable.table:
                                if identi in symboltable.table[str(symboltable.level[:-loop])]:
                                    templev = symboltable.level[:-loop]
                                    break
                                loop += 1
                    if templev == []:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], identi+" can't be found")
                    else:
                        templev.append(identi)
                    nextToken = token.PeekNextToken()
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "']' expected at this area")
            if nextToken[0] == "=":
                nextToken = token.GetNextToken()
                tempexpss=tempexp
                tempexp = ""
                expression(token)
                if containsList:
                    writePop('temp', 0)
                    writePop('pointer', 1)
                    writePush('temp', 0)
                    writePop('that', 0)
                else:
                    if len(res) == 2:
                        writePop(res[0][1], res[0][3])
                    else:
                        writePop(res[1], res[3])
                if not containsList:
                    try:
                        if tempexp == ftype:
                            pass
                        elif str(type(eval(tempexp))) == "<class '"+ftype+"'>":
                            pass
                        elif str(type(eval(tempexp))) == "<class 'bool'>" and ftype == "boolean":
                            pass
                        elif str(type(eval(tempexp))) == "<class 'int'>" and ftype == "char":
                            pass
                        elif str(type(eval(tempexp))) == "<class 'float'>" and ftype == "int":
                            pass
                        else:
                            raise Exception('Semantic', token.line+1,
                                            token.code[token.line][token.pointer-1], "wrong type for assignment")
                    except Exception:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], "wrong type for assignment")
                else:
                    ftype = ""
                    try:
                        if eval(tempexp) == None:
                            result = 0
                            tempexps = tempexp
                            tempexp = "result="+tempexp
                            eval(tempexp)
                            ftype = str(type(result)).replace(
                                "<class '", "").replace("'>", "")
                        else:
                            ftype = tempexp.replace(
                                "<class '", "").replace("'>", "")
                    except Exception:
                        ftype = tempexp
                    templ = symboltable.level[:]
                    symboltable.level = templev[:]
                    symboltable.Add("Array", ftype, fkind, True, True, False)
                    symboltable.level = templ[:]
                nextToken = token.GetNextToken()
                if nextToken[0] == ";":
                    pass
                else:
                    raise Exception(
                        'Syntax', token.line+1, token.code[token.line][token.pointer-1], "';' expected at this area")
                tempexp=tempexpss
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
    global labelNum
    nextToken = token.GetNextToken()
    if nextToken[0] == "if":
        trueLabel = "IF_TRUE" + str(labelNum)
        falseLabel = "IF_FALSE" + str(labelNum)
        endLabel = "IF_END" + str(labelNum)
        nextToken = token.GetNextToken()
        if nextToken[0] == "(":
            expression(token)
            nextToken = token.GetNextToken()
            writeIf(trueLabel)
            writeGoto(falseLabel)
            writeLabel(trueLabel)
            if nextToken[0] == ")":
                symboltable.level.append("if"+str(labelNum))
                labelNum += 1
                nextToken = token.GetNextToken()
                if nextToken[0] == "{":
                    while statementTest(token):
                        statement(token)
                    nextToken = token.GetNextToken()
                    if nextToken[0] == "}":
                        del symboltable.level[-1]
                        nextToken = token.PeekNextToken()
                        if nextToken[0] == "else":
                            writeGoto(endLabel)
                            writeLabel(falseLabel)
                            writeLabel(endLabel)
                            symboltable.level.append("else"+str(labelNum-1))
                            nextToken = token.GetNextToken()
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
                            writeLabel(falseLabel)
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
    global labelNum
    nextToken = token.GetNextToken()
    if nextToken[0] == "while":
        nextToken = token.GetNextToken()
        if nextToken[0] == "(":
            writeLabel('WHILE_EXP'+str(labelNum))
            expression(token)
            writeArithmetic('not')
            nextToken = token.GetNextToken()
            if nextToken[0] == ")":
                writeIf('WHILE_END'+str(labelNum))
                symboltable.level.append("while"+str(labelNum))
                labelNum += 1
                nextToken = token.GetNextToken()
                if nextToken[0] == "{":
                    while statementTest(token):
                        statement(token)
                    nextToken = token.GetNextToken()
                    writeGoto('WHILE_EXP'+str(labelNum))
                    writeLabel('WHILE_END'+str(labelNum))
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
        writePop('temp', 0)
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
    global tempexp
    nextToken = token.GetNextToken()
    isObjorClass = False
    isExpress=False
    if nextToken[1] == "Identifier":
        ident = [nextToken[0]]
        sub_identifier = ""
        nextToken = token.GetNextToken()
        if nextToken[0] == ".":
            isObjorClass = True
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                if str([ident[0]]) in symboltable.table:
                    pass
                else:
                    res=symboltable.Find(ident[0])
                    if not res:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], ident[0]+" can't be found")
                    elif len(res) == 2:
                        ident[0]= res[0][0]
                        isExpress=True
                    else:
                        ident[0] = res[0]
                        isExpress=True
                if nextToken[0] in symboltable.table[str(ident)]:
                    sub_identifier = nextToken[0]
                    ident.append(nextToken[0])
                else:
                    raise Exception('Semantic', token.line+1,
                                    token.code[token.line][token.pointer-1], nextToken[0]+" can't be found")
                nextToken = token.GetNextToken()
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "an identifier expected at this area")
        if nextToken[0] == "(":
            tempexpss=tempexp
            tempexp = ""
            expressionList(token, ident)
            nextToken = token.GetNextToken()
            if nextToken[0] == ")":
                callName = ""
                if isObjorClass:
                    global numExpressions
                    callName = ident[0] + "." + sub_identifier
                    if isExpress:
                        numExpressions += 1
                    writeCall(callName, numExpressions)
                    # if there is only 1 identifer and it is a method,
                    # push it on to the stack first as first param
                else:
                    if isExpress:
                        res=symboltable.Find(ident[0])
                        if len(res) == 2:
                            writePush(res[0][1], res[0][4])
                        else:
                            writePush(res[1], res[4])
                    else:
                        writePush('pointer', 0)
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
            tempexp=tempexpss
        else:
            raise Exception(
                'Syntax', token.line+1, token.code[token.line][token.pointer-1], "'(' expected at this area")
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "an identifier expected at this area")


def expressionList(token, function):
    global tempexp
    tempexpss = tempexp
    tempexp = ""
    argu = {}
    argulist = {}
    if str(function) in symboltable.table:
        argulist = symboltable.table[str(function)]
        for key in argulist:
            if argulist[key][1] != 'argument':
                continue
            argu[str(argulist[key][3])] = argulist[key][0]
        argcount = 0
        if factorTest(token):
            expression(token)
            if len(argu) > argcount:
                try:
                    if tempexp == argu[str(argcount)]:
                        pass
                    elif str(type(eval(tempexp))) == "<class '"+argu[str(argcount)]+"'>":
                        pass
                    elif str(type(eval(tempexp))) == "<class 'bool'>" and argu[str(argcount)] == "boolean":
                        pass
                    elif str(type(eval(tempexp))) == "<class 'int'>" and argu[str(argcount)] == "char":
                        pass
                    elif str(type(eval(tempexp))) == "<class 'float'>" and argu[str(argcount)] == "int":
                        pass
                    else:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], "wrong given argument value type")
                except Exception:
                    raise Exception('Semantic', token.line+1,
                                    token.code[token.line][token.pointer-1], "wrong given argument value type")
            else:
                raise Exception('Semantic', token.line+1,
                                token.code[token.line][token.pointer-1], "wrong given argument number")

            while True:
                nextToken = token.PeekNextToken()
                if nextToken[0] == ",":
                    argcount += 1
                    tempexp = ""
                    nextToken = token.GetNextToken()
                    expression(token)
                    if len(argu) > argcount:
                        try:
                            if tempexp == argu[str(argcount)]:
                                pass
                            elif str(type(eval(tempexp))) == "<class '"+argu[str(argcount)]+"'>":
                                pass
                            elif str(type(eval(tempexp))) == "<class 'bool'>" and argu[str(argcount)] == "boolean":
                                pass
                            elif str(type(eval(tempexp))) == "<class 'int'>" and argu[str(argcount)] == "char":
                                pass
                            elif str(type(eval(tempexp))) == "<class 'float'>" and argu[str(argcount)] == "int":
                                pass
                            else:
                                raise Exception('Semantic', token.line+1,
                                                token.code[token.line][token.pointer-1], "wrong given argument value type")
                        except Exception:
                            raise Exception('Semantic', token.line+1,
                                            token.code[token.line][token.pointer-1], "wrong given argument value type")
                    else:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], "wrong given argument number")
                else:
                    break
    else:
        pass
    tempexp = tempexpss


def returnStatement(token):
    global tempexp
    nextToken = token.GetNextToken()
    ftype = ""
    if nextToken[0] == "return":
        writeReturn()
        if str(symboltable.level) in symboltable.table:
            if symboltable.level[-1] in symboltable.table[str(symboltable.level)]:
                ftype = symboltable.table[str(symboltable.level)][symboltable.level[-1]][0]
        loop = 1
        while loop < len(symboltable.level) and ftype=="":
            if str(symboltable.level[:-loop]) in symboltable.table:
                if symboltable.level[-loop-1] in symboltable.table[str(symboltable.level[:-loop])]:
                    ftype = symboltable.table[str(symboltable.level[:-loop])][symboltable.level[-loop-1]][0]
                    break
            loop += 1
        tempexpss=tempexp
        tempexp = ""
        if factorTest(token):
            expression(token)
        try:
            if tempexp == "" and ftype == "void":
                pass
            elif tempexp == ftype:
                pass
            elif str(type(eval(tempexp))) == "<class '"+ftype+"'>":
                pass
            elif str(type(eval(tempexp))) == "<class 'bool'>" and ftype == "boolean":
                pass
            elif str(type(eval(tempexp))) == "<class 'int'>" and ftype == "char":
                pass
            elif str(type(eval(tempexp))) == "<class 'float'>" and ftype == "int":
                pass
            else:
                raise Exception('Semantic', token.line+1,
                                token.code[token.line][token.pointer-1], "wrong return type")
        except Exception:
            raise Exception('Semantic', token.line+1,
                            token.code[token.line][token.pointer-1], "wrong return type")
        tempexp=tempexpss
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
    global tempexp
    if factorTest(token):
        relationalExpression(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '&' or nextToken[0] == '|':
            tempexp += nextToken[0]
            writeArithmetic(VM_OPERATORS[nextToken[0]])
            nextToken = token.GetNextToken()
            relationalExpression(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a relational expression at this area")


def relationalExpression(token):
    global tempexp
    if factorTest(token):
        arithmeticExpression(token)
        nextToken = token.PeekNextToken()
        while True:
            # I think the provided full jack grammar make a mistake here, so I correct it.
            if nextToken[0] == "=":
                tempexp += nextToken[0]
                writeArithmetic(VM_OPERATORS[nextToken[0]])
                nextToken = token.GetNextToken()
                arithmeticExpression(token)
                nextToken = token.PeekNextToken()
            elif nextToken[0] == '>' or nextToken[0] == '<':
                tempexp += nextToken[0]
                writeArithmetic(VM_OPERATORS[nextToken[0]])
                nextToken = token.GetNextToken()
                nextToken = token.PeekNextToken()
                if nextToken[0] == "=":
                    tempexp += nextToken[0]
                    writeArithmetic(VM_OPERATORS[nextToken[0]])
                    nextToken = token.GetNextToken()
                arithmeticExpression(token)
                nextToken = token.PeekNextToken()
            else:
                break
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a arithmetic expression at this area")


def arithmeticExpression(token):
    global tempexp
    if factorTest(token):
        term(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '+' or nextToken[0] == '-':
            tempexp += nextToken[0]
            writeArithmetic(VM_OPERATORS[nextToken[0]])
            nextToken = token.GetNextToken()
            term(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a term at this area")


def term(token):
    global tempexp
    if factorTest(token):
        factor(token)
        nextToken = token.PeekNextToken()
        while nextToken[0] == '*' or nextToken[0] == '/':
            tempexp += nextToken[0]
            writeArithmetic(VM_OPERATORS[nextToken[0]])
            nextToken = token.GetNextToken()
            factor(token)
            nextToken = token.PeekNextToken()
    else:
        raise Exception('Syntax', token.line+1,
                        token.code[token.line][token.pointer-1], "expect a factor at this area")


def factor(token):
    global tempexp
    nextToken = token.PeekNextToken()
    if nextToken[0] == '-' or nextToken[0] == '~':
        tempexp += nextToken[0]
        writeArithmetic(UNARY_OPERATORS[nextToken[0]])
        nextToken = token.GetNextToken()
    nextToken = token.GetNextToken()
    if nextToken[1] == 'Integer' or nextToken[1] == 'String' or nextToken[0] == 'true' or nextToken[0] == 'false' or nextToken[0] == 'null':
        if nextToken[0] == 'true':
            tempexp += 'True'
            writePush('constant', 0)
            writeArithmetic('not')
        elif nextToken[0] == 'false':
            tempexp += 'False'
            writePush('constant', 1)
        elif nextToken[0] == 'null':
            tempexp += 'None'
        else:
            if nextToken[1] == 'String':
                if tempexp != "":
                    raise Exception('Semantic', token.line+1,
                                    token.code[token.line][token.pointer-1], " wrong expression!")
                else:
                    tempexp = "String"
            else:
                tempexp += str(nextToken[0])
        if nextToken[1] == 'Integer':
            writePush('constant', nextToken[0])
        elif nextToken[1] == 'String':
            writePush('constant', len(nextToken[0]))
            writeCall('String.new', 1)
            for i in range(len(nextToken[0])):
                writePush('constant', ord(nextToken[0][i]))
                writeCall('String.appendChar', 2)
    elif nextToken[1] == 'Identifier' or nextToken[0] == 'this':
        ident = []
        if nextToken[1] == 'Identifier':
            ident = [nextToken[0]]
        else:
            global tempclassN
            ident = [tempclassN]
        nextToken = token.PeekNextToken()
        dot = False
        if nextToken[0] == '.':
            nextToken = token.GetNextToken()
            nextToken = token.GetNextToken()
            if nextToken[1] == "Identifier":
                dot = True
                if str([ident[0]]) in symboltable.table:
                    pass
                else:
                    res=symboltable.Find(ident[0])
                    if not res:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], ident[0]+" can't be found")
                    elif len(res) == 2:
                        ident[0] = res[0][0]
                    else:
                        ident[0] = res[0]
                if nextToken[0] in symboltable.table[str(ident)]:
                    ident.append(nextToken[0])
                else:
                    raise Exception('Semantic', token.line+1,
                                    token.code[token.line][token.pointer-1], nextToken[0]+" can't be found")
                nextToken = token.PeekNextToken()
                if nextToken[0] == "(":
                    nextToken = token.GetNextToken()
                    if nextToken[0] == ")":
                        pass
                    else:
                        expressionList(token, ident)
                        nextToken = token.GetNextToken()
                        if nextToken[0] == ")":
                            pass
                        else:
                            raise Exception('Syntax', token.line+1,
                                            token.code[token.line][token.pointer-1], " ')' expect here")
                    if ident[-1] in symboltable.table[str([ident[0]])]:
                        res = symboltable.table[str([ident[0]])][ident[-1]]
                        if res[0] == "int" or res[0] == "char":
                            tempexp += "1"
                        elif res[0] == "boolean":
                            tempexp += "True"
                        else:
                            tempexp += res[0]
                    else:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], ident[-1]+" can't be found")
                else:
                    if ident[-1] in symboltable.table[str([ident[0]])]:
                        res = symboltable.table[str([ident[0]])][ident[-1]]
                        if res[0] == "int" or res[0] == "char":
                            tempexp += "1"
                        elif res[0] == "boolean":
                            tempexp += "True"
                        else:
                            tempexp += res[0]
                    else:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], ident[-1]+" can't be found")
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "expect a identifier at this area")
        if nextToken[0] == '[':
            ident.append("Array")
            tempexps = tempexp
            tempexp = ""
            nextToken = token.GetNextToken()
            expression(token)
            tempexp = tempexps
            nextToken = token.GetNextToken()
            if nextToken[0] == ']':
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "']' expected at this area")
        if nextToken[0] == '(':
            tempexps = tempexp
            tempexp = ""
            nextToken = token.GetNextToken()
            expressionList(token, ident)
            tempexp = tempexps
            nextToken = token.GetNextToken()
            if nextToken[0] == ')':
                pass
            else:
                raise Exception(
                    'Syntax', token.line+1, token.code[token.line][token.pointer-1], "')' expected at this area")
        if not dot:
            if str(ident) in symboltable.table:
                    tempexp += ident[0]
            elif len(ident) == 1 or (len(ident) == 2 and ident[-1] == "Array"):
                res = symboltable.Find(ident[0])
                templev = []
                if len(ident) != 1:
                    mark = False
                    if str(symboltable.level) in symboltable.table:
                        if ident[0] in symboltable.table[str(symboltable.level)]:
                            templev = symboltable.level[:]
                            mark = True
                    if not mark:
                        loop = 1
                        while loop < len(symboltable.level):
                            if str(symboltable.level[:-loop]) in symboltable.table:
                                if ident[0] in symboltable.table[str(symboltable.level[:-loop])]:
                                    templev = symboltable.level[:-loop]
                                    break
                                loop += 1

                    if templev == []:
                        raise Exception('Semantic', token.line+1,
                                        token.code[token.line][token.pointer-1], ident[-1]+" can't be found")
                    else:
                        templev.append(ident[0])
                        if str(templev) in symboltable.table:
                            if "Array" in symboltable.table[str(templev)]:
                                res = symboltable.table[str(templev)]["Array"]
                            else:
                                raise Exception('Semantic', token.line+1,
                                                token.code[token.line][token.pointer-1], "Array can't be found")
                        else:
                            raise Exception('Semantic', token.line+1,
                                            token.code[token.line][token.pointer-1], ident[0]+" can't be found")
                if not res:
                    raise Exception('Semantic', token.line+1,
                                    token.code[token.line][token.pointer-1], ident[-1]+" can't be found")
                else:
                    if len(res) == 2:
                        if res[0][0] == "int" or res[0][0] == "char":
                            tempexp += "1"
                        elif res[0][0] == "boolean":
                            tempexp += "True"
                        else:
                            tempexp += res[0][0]
                    else:
                        if res[0] == "int" or res[0] == "char":
                            tempexp += "1"
                        elif res[0] == "boolean":
                            tempexp += "True"
                        else:
                            tempexp += res[0]
            else:
                raise Exception('Semantic', token.line+1,
                                token.code[token.line][token.pointer-1], ident[-1]+" can't be found")
    elif nextToken[0] == '(':
        tempexp += "("
        expression(token)
        nextToken = token.GetNextToken()
        if nextToken[0] == ')':
            tempexp += ")"
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
