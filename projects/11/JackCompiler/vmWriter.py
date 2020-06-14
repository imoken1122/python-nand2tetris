class VMWriter:
    def __init__(self):
        self.vm_code = []

    def writePush(self,segment,index):
        temp = f'push {segment} {index}'
        self.vm_code.append(temp)

    def writePop(self,segment,index):
        temp = f'pop {segment} {index}'
        self.vm_code.append(temp)

    def writeArithmetic(self,cmd):
        self.vm_code.append(f'{cmd}')

    def writeLable(self,lable):
        self.vm_code.append(f'label {lable}')

    def writeGoto(self,lable):
        self.vm_code.append(f'goto {lable}')

    def writeIf(self,lable):
        self.vm_code.append(f'if-goto {lable}')

    def writeCall(self,name,nArgs):
        self.vm_code.append(f'call {name} {nArgs}')

    def writeFunction(self,name,nLocals):
        self.vm_code.append(f'function {name} {nLocals}')

    def writeReturn(self):
        self.vm_code.append('return')
    
    def getVMCode(self):
        return self.vm_code