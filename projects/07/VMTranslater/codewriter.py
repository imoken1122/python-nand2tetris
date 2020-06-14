import re
DEFINE_RAM = {'local':'LCL','argument':'ARG','this':'THIS','that':'THAT','temp':5,'pointer':3}
ArithmetricDic = {'add':'D=D+M',
                'sub':'D=M-D', # x-y
                'neg':'D=-M',
                'not':'D=!M',
                'eq': 'JEQ', #out=0
                'gt': 'JGT', # out > 0
                'lt':'JLT', # out < 0
                'and': 'D=D&M',
                'or': 'D=D|M'}
class CodeWriter(object):
    def __init__(self,file):
        self.filename = file
        self.asm_code = []
        self.jump_lable = 0
    def writeArithmetic(self,cmd):

        if cmd in ['add','sub','and','or']:
            
            self.pop_to_A() # y
            self.asm_code += ['D=M']
            self.pop_to_A() # x
            self.asm_code += [ArithmetricDic[cmd]]
            self.push_from_D()
        elif cmd in ['neg','not']:
            self.pop_to_A()
            self.asm_code += [ArithmetricDic[cmd]]
            self.push_from_D()
        else: 
            self.pop_to_A() # y 
            self.asm_code += ['D=M']
            self.pop_to_A() #x
            temp = [
                'D=M-D', # x-y
               f'@JUMP_TRUE_{self.jump_lable}',
                f'D;{ArithmetricDic[cmd]}',
                'D=0',
                f'@JUMP_FALSE_{self.jump_lable}',
                '0;JMP',
              f'(JUMP_TRUE_{self.jump_lable})',
                'D=-1', #TrueのときはD=-1
                f'(JUMP_FALSE_{self.jump_lable})'
            ]
            self.asm_code += temp
            self.push_from_D() 
            self.jump_lable +=  1
    def pop_to_A(self):
        temp = ['@SP','M=M-1','A=M']
        self.asm_code += temp
    def push_from_D(self,):
        temp = ['@SP','A=M','M=D','@SP','M=M+1']
        self.asm_code += temp
    def wirtePushPop(self,cmdtype,segment,idx):
        if cmdtype == 'C_PUSH':
            if segment == 'constant':
                temp = [f'@{idx}','D=A']

            elif segment in ['local', 'argument','this','that']:
                temp = [f'@{DEFINE_RAM[segment]}','A=M']
                if re.search('A-Za-z',idx) == None:
                    temp += ['A=A+1']*int(idx)
                temp += ['D=M'] # indexの数だけアドレスを移動する

            elif segment in ['temp','pointer']:
                temp = [f'@{DEFINE_RAM[segment]}']
                if re.search('A-Za-z',idx) == None:
                    temp += ['A=A+1']*int(idx)# pointerは3,4,tempは5-15をaddressとしたメモリ値
                temp += ['D=M'] 

            elif segment =='static':
                temp = [f'@{self.filename}.{idx}','D=M']
            
            self.asm_code += temp
            self.push_from_D()

        elif cmdtype == 'C_POP':

            self.pop_to_A() # SPのアドレスにある値
            if segment in ['local', 'argument','this','that']:
                temp = ['D=M',f'@{DEFINE_RAM[segment]}','A=M']
                if re.search('A-Za-z',idx) == None:
                    temp += ['A=A+1']*int(idx) # indexの数だけアドレスを移動する
                temp += ['M=D'] 
            elif segment in ['temp','pointer']:
                temp = ['D=M',f'@{DEFINE_RAM[segment]}']
                if re.search('A-Za-z',idx) == None:
                    temp += ['A=A+1']*int(idx) # pointerは2,4,tempは5-15をaddressとしたメモリ値
                temp += ['M=D'] 

            elif segment =='static':
                temp = ['D=M',f'@{self.filename}.{idx}','M=D'] 

            self.asm_code += temp
    def fileToOutput(self):
        with open(self.filename+'.asm','w') as f:
            for i in self.asm_code:
                f.writelines(i+'\n')
        