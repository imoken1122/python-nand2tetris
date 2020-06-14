from parser import Parser
from codewriter import CodeWriter
import sys
import re


if __name__ == "__main__":
    path = sys.argv[1]
    codewriter = CodeWriter(path)
    parser = Parser(path)

    while parser.hasMoreCommands():
        parser.advance()
        print(parser.current_cmd)
        cmdtype = parser.commandType()
        arg1 = parser.arg1()
        if cmdtype == 'C_ARITHMETIC':
            codewriter.writeArithmetic(arg1)
        elif cmdtype in ['C_PUSH','C_POP']:
            arg2 = parser.arg2()
            codewriter.wirtePushPop(cmdtype,arg1,arg2)

    codewriter.fileToOutput()
