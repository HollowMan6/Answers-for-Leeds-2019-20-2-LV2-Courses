#!/usr/bin/python3
# By Hollow Man

import sys
import os
import lexer
import jcparser
import copy
import SymbolTable

# When having no argument
if len(sys.argv) == 1:
    print("Error, no input directory")
# When having 2 or more arguments
elif len(sys.argv) > 2:
    print("Error, too many arguments, please only type your JACK program directory")
else:
    # Check whether the folder typed exists
    if not os.path.exists(sys.argv[1]):
        print("Error, please make sure your typed JACK program directory exists")
    # Check whether the name typed is a folder
    elif os.path.isfile(sys.argv[1]):
        print("Error, please type your JACK program directory instead of file name")
    else:
        filename = os.listdir()
        # Record the jack file number so that later on it can avoid no jack files in the folder
        count = 0
        # Load system library
        systab={}
        for fpathe, dirs, fs in os.walk("syslib"):
            for f in fs:
                file = os.path.join(fpathe, f)
                if os.path.splitext(f)[1] == ".jack":
                    source = open(file)
                    # Read Source Code
                    sourcecode = []
                    temp = source.readline()
                    while temp:
                        sourcecode.append(temp.replace("\n", ""))
                        temp = source.readline()
                    source.close()
                    tokens = lexer.Token(sourcecode)
                    try:
                        tokens.line = 0
                        tokens.pointer = 0
                        systab=SymbolTable.start(tokens,systab)
                    # Give error infomation
                    except Exception as err:
                        print(file,end="")
                        print(err.args[0]+" error, line "+str(err.args[1]) +
                                ', close to "'+str(err.args[2])+'", '+str(err.args[3]))
            for f in fs:
                file = os.path.join(fpathe, f)
                if os.path.splitext(f)[1] == ".jack":
                    source = open(file)
                    # Read Source Code
                    sourcecode = []
                    temp = source.readline()
                    while temp:
                        sourcecode.append(temp.replace("\n", ""))
                        temp = source.readline()
                    source.close()
                    # Compile begin
                    print("\nCompiling System library: "+file)
                    tokens = lexer.Token(sourcecode)
                    try:
                        tokens.line = 0
                        tokens.pointer = 0
                        systab=jcparser.start(tokens,systab,True)
                        print("Compilation success")
                    # Give error infomation
                    except Exception as err:
                        try:
                            print(err.args[0]+" error, line "+str(err.args[1]) +
                                ', close to "'+str(err.args[2])+'", '+str(err.args[3]))
                        except Exception:
                            print("Unkown Error")
        for fpathe, dirs, fs in os.walk(sys.argv[1]):
            stab=copy.deepcopy(systab)
            for f in fs:
                file = os.path.join(fpathe, f)
                if os.path.splitext(f)[1] == ".jack":
                    source = open(file)
                    # Read Source Code
                    sourcecode = []
                    temp = source.readline()
                    while temp:
                        sourcecode.append(temp.replace("\n", ""))
                        temp = source.readline()
                    source.close()
                    tokens = lexer.Token(sourcecode)
                    try:
                        tokens.line = 0
                        tokens.pointer = 0
                        stab=SymbolTable.start(tokens,stab)
                    # Give error infomation
                    except Exception as err:
                        print(file,end="")
                        print(err.args[0]+" error, line "+str(err.args[1]) +
                                ', close to "'+str(err.args[2])+'", '+str(err.args[3]))
            for f in fs:
                file = os.path.join(fpathe, f)
                if os.path.splitext(f)[1] == ".jack":
                    count += 1
                    source = open(file)
                    # Read Source Code
                    sourcecode = []
                    temp = source.readline()
                    while temp:
                        sourcecode.append(temp.replace("\n", ""))
                        temp = source.readline()
                    source.close()
                    # Compile begin
                    print("\nCompiling "+file)
                    tokens = lexer.Token(sourcecode)
                    try:
                        destcode = ""
                        tokens.line = 0
                        tokens.pointer = 0
                        destcode,stab = jcparser.start(tokens,stab)
                        print("Compilation success")
                        with open(os.path.join(fpathe, os.path.splitext(f)[0]+".vm"), 'w') as dest:
                            dest.write(destcode)
                    # Give error infomation
                    except Exception as err:
                        try:
                            print(err.args[0]+" error, line "+str(err.args[1]) +
                                ', close to "'+str(err.args[2])+'", '+str(err.args[3]))
                        except Exception:
                            print("Unkown Error")
                    # Write Generated Code
        if count == 0:
            print("Error, unable to find any jack source files in your typed JACK program directory, "
                  "please make sure your source code files have .jack extension")
        # Compiling finish
        else:
            print("\nCompilation Complete! Proceed " +
                  str(count)+" files in total.")
