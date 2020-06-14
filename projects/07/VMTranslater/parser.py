import re
class Parser:
    def __init__(self,file) -> None:
        with open(file+'.vm',"r") as f:
            self.vm_code = []
            for i in f.readlines():
                if i[0] == '/' or len(i) == 1:
                    continue 
                temp = re.sub('(//.*|\n)','',i)
                temp = temp.split(' ')
                self.vm_code.append(temp)
                
        self.current_idx = -1
        self.current_cmd = None
        self.len_cmd = len(self.vm_code)

    def hasMoreCommands(self):
        if self.len_cmd-1 != self.current_idx:
            return 1
        else: return 0  
    
    def advance(self):
        self.current_idx +=1
        self.current_cmd = self.vm_code[self.current_idx] 
        

    def commandType(self):
        cmd = ' '.join(self.current_cmd)
        if re.search('push',cmd) != None:
            return 'C_PUSH'
        elif re.search('pop',cmd) != None:
            return 'C_POP'
        elif re.search('label',cmd) != None:
            return  'C_LABEL'
        elif re.search('if',cmd) !=None:
            return 'C_IF'
        elif re.search('goto',cmd) != None:
            return 'C_GOTO'
        elif re.search('function',cmd) != None:
            return 'C_FUNCTION'
        elif re.search('return',cmd) != None:
            return 'C_RETURN'
        elif re.search('call',cmd) != None:
            return 'C_CALL'
        else: return 'C_ARITHMETIC'


    def arg1(self):
        if len(self.current_cmd) == 1:
            return self.current_cmd[0]
        else:
            return self.current_cmd[1]
    def arg2(self):
        return self.current_cmd[2]