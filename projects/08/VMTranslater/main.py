import os
from parser import Parser
from codewriter import CodeWriter
import sys
import re
def vm2asm_translater(codewriter, parser,):
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
        elif cmdtype =='C_LABEL':
            codewriter.writeLabel(arg1)
        elif cmdtype =='C_IF':
            codewriter.writeIf(arg1)
        elif cmdtype =='C_GOTO':
            codewriter.writeGoto(arg1)
        elif cmdtype == 'C_FUNCTION':
            arg2 = int(parser.arg2())
            codewriter.writeFunction(arg1,arg2)
        elif cmdtype == 'C_RETURN':
            codewriter.writeReturn()
        elif cmdtype == 'C_CALL':
            arg2 = int(parser.arg2())
            codewriter.writeCall(arg1,arg2)

    return codewriter.asm_code


def fileToOutput(filename,asm_code):
    with open(f'./{filename}/{filename}.asm','w') as f:
        for i in asm_code:
            f.writelines(i+'\n')
    
def get_init_flag(path):
    if re.search('Sys',path) != None:
        return 1
    else:return 0
if __name__ == "__main__":

    path,flag = sys.argv[1],int(sys.argv[2]), # dir name existing .vm file, wheather exist many file(1) or not(0)
    allasm_code = []

    if flag == 0:
        f_list = list(map(lambda x: path +'/'+x,os.listdir(path)))
        file = [f for f in f_list if re.search('.vm',f)!= None][0][:-3]
        init_flag = get_init_flag(file)
        codewriter = CodeWriter(file,init_flag)
        parser = Parser(file)
        allasm_code += vm2asm_translater(codewriter,parser)
    else: 
        old_return_addr = 0
        old_labelNum =0 
        init_flag =1  
        f_list = list(map(lambda x: path +'/'+x,os.listdir(path)))
        for f in f_list:
            if re.search('.*\.vm',f) !=None:
                file = re.sub('\.vm','',f)
                codewriter = CodeWriter(file,init_flag)
                parser = Parser(file)
                codewriter.labelNum = old_labelNum
                codewriter.return_address = old_return_addr
                allasm_code += vm2asm_translater(codewriter,parser)
                old_labelNum = codewriter.labelNum # save old lable
                old_return_addr = codewriter.return_address # save old address
                init_flag = 0

    fileToOutput(path, allasm_code)