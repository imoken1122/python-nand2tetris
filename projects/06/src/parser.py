import re
class Parser:
    def __init__(self,file_path):
        with open(file_path,"r") as f:
            
            self.asseble_code = []
            for i in f.readlines():
                if i[0] == "/" or len(i)==1:
                    continue
                temp = re.sub("(//.*|\s)","",i)
                self.asseble_code.append(temp)

        self.cmd_idx = -1
        self.current_cmd = None
        self.len_cmd = len(self.asseble_code)
    def reset_idx(self):
        self.cmd_idx=-1
    def hasMoreCommands(self):
        if self.len_cmd-1 != self.cmd_idx:
            return 1
        else : return 0

    def advance(self,):

        self.cmd_idx += 1
        self.current_cmd = self.asseble_code[self.cmd_idx]


    def commandType(self):
        if re.search("@",self.current_cmd) != None:
            return "A_COMMAND"
        elif re.search("(=|;)",self.current_cmd) != None:
            return "C_COMMAND"
        else: return "L_COMMAND"

    def symbol(self):
        return re.sub("(@|\(|\))","",self.current_cmd)
    def dest(self):
        temp = self.current_cmd.split("=")
        if len(temp)==1:
            return "null" 
        else: return temp[0]
    def comp(self):
        return re.sub("(.*=|;.*)","",self.current_cmd)
    def jump(self):
        temp = self.current_cmd.split(";")
        if len(temp) == 1: 
            return "null"
        else: return temp[1]