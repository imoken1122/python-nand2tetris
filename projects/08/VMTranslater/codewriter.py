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
    def __init__(self,file,init_flag):
        if re.search('/',file) != None:
            self.filename = re.sub('.*/','',file)
        else:   
            self.filename = file
        self.asm_code = []
        self.jump_lable = 0
        self.return_address = 0
        if init_flag:
            self.writeInit()
    def writeInit(self):
        temp = ['@256','D=A','@SP','M=D']
        self.asm_code += temp
        self.writeCall('Sys.init',0)
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

    def writeLabel(self, label):
        temp = [f'({label})']
        self.asm_code += temp

    def writeGoto(self, label):
        temp = [f'@{label}','0;JMP']
        self.asm_code += temp

    def writeIf(self,label):
        self.pop_to_A()
        temp = ['D=M',f'@{label}','D;JNE']
        self.asm_code += temp
    
    def writeCall(self,function_name, numArgs):

        self.asm_code += [f'@RETURN_ADDRESS_{self.return_address}','D=A']
        self.push_from_D()

        self.asm_code += ['@LCL','D=M']
        self.push_from_D()

        self.asm_code +=['@ARG','D=M']
        self.push_from_D()

        self.asm_code += ['@THIS','D=M']
        self.push_from_D()

        self.asm_code += ['@THAT','D=M']
        self.push_from_D()

        temp = [
            '@SP',
            'D=M',
            f'@{numArgs}',
            'D=D-A',
            '@5',
            'D=D-A',
            '@ARG',
            'M=D',
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
            f'@{function_name}',
            '0;JMP',
            f'(RETURN_ADDRESS_{self.return_address})'
        ]
        self.asm_code += temp

        self.return_address += 1


    def writeReturn(self):
        temp = [
            '@LCL',
            'D=M',
            '@R13', # FRAME格納
            'M=D',
            '@5', 
            'D=A',
            '@R13', 
            'A=M-D', # FRAME(LCLのベースアドレス) -5
            'D=M', #リターンアドレス
            '@R14', # RET
            'M=D'
        ]
        self.asm_code += temp

        self.pop_to_A() #戻り値があるアドレス
        temp = [
            'D=M', #戻り値
            '@ARG',
            'A=M',
            'M=D', #*ARG=pop()

            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',

            '@R13', #SP
            'AM=M-1', #SP-1
            'D=M', # D = M[SP-1]
            '@THAT',
            'M=D', # THAT=*(FRAME-1)

            '@R13', #SP
            'AM=M-1', #SP-2
            'D=M', # D = M[SP-2]
            '@THIS',
            'M=D', # THIS=*(FRAME-2)
            
            '@R13', #SP
            'AM=M-1', #SP-3
            'D=M', # D = M[SP-3]
            '@ARG',
            'M=D', # THAT=*(FRAME-3)

            '@R13', #SP
            'AM=M-1', #SP-4
            'D=M', # D = M[SP-4]
            '@LCL',
            'M=D', # THAT=*(FRAME-4)

            '@R14',
            'A=M',
            '0;JMP'
        ]
        self.asm_code += temp

    def writeFunction(self,function_name, numLocals):
        temp = [
            f'({function_name})',
            'D=0']
        self.asm_code += temp
    
        for _ in range(numLocals):
            self.push_from_D()

        
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
        