import json
import re

keyword_list = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
class JackTokenizer:
    def __init__(self, filename):
        self.code = []
        with open(filename, 'r') as f:
            for i in f.readlines():
                if i[0] == '/' or len(i) == 1:
                    continue 
                temp = re.sub('(^\s?\*.*|//.*|/\*.*\*/|\n|\t| {2,})','',i)

                self.code.append(temp)

        self.token_list = []
        reg = '([\{\}\(\)\[\]\.,;\+\-\*\/&\|<>=~])'
        for c in self.code:
            flag = 0
            if re.search('"',c) != None:
                quat_idx = list(re.finditer('"',c))
                quat_idx = list(map(lambda x: x.span(),quat_idx))
                s,e = quat_idx
                groundtrue_str =c[s[0]:e[1]] 
                c = c.replace(groundtrue_str,' replace_str ')
                temp = c.split(' ')

            else:
                temp=c.split(' ')

            for cc in temp:
                singular_idx = list(re.finditer('(\+\+|--|[^A-Za-z]=)',cc)) # get index <=,>=,++.==,--,+= ...etc
                if len(singular_idx) != 0:
                    s,e = singular_idx[0].span() # ex. index of < and =.  (s and e) 
                    parse = re.split(reg,cc[:s]) + [cc[s:e]] + re.split(reg,cc[e:]) # concat cc[:s]+ <= + cc[e:]
                    flag = 1
                elif cc == 'replace_str':
                    parse = [groundtrue_str]
                    
                elif flag == 1: 
                    flag=0
                    continue
                else:
                    parse = re.split(reg,cc) # simple split by char contain to reg
                parse= list(filter(lambda x : x!='',parse)) 
                self.token_list += parse
                
        self.current_idx = 0 
        self.current_token = self.token_list[self.current_idx] 
        self.len_ctx = len(self.token_list)
    def hasMoreCommands(self):
        if self.len_ctx-1 != self.current_idx:
            return 1
        else: return 0  
    
    def advance(self):
        
        self.current_idx +=1
        #print(self.current_idx,self.len_ctx,len(self.token_list))
        self.current_token = self.token_list[self.current_idx] 
        
    def tokenType(self):
        if self.current_token in keyword_list:
            return 'KEYWORDS'
        elif self.current_token in symbol_list:
            return 'SYMBOLS'
        elif re.search('^[0-9]+?',self.current_token)!=None and (0<=int(self.current_token) or int(self.current_token) <= 32767):
            return 'INT_CONST'
        elif re.search('^"[^"\n]*"$',self.current_token) != None:
            return 'STRING_CONST'
        elif re.search('^[a-zA-Z_][a-zA-Z0-9_]*$',self.current_token) != None:

            return 'IDENTIFIER'  
    

    def keyword(self):
        return self.current_token
        

    def symbol(self):
        return self.current_token 

    def identifier(self):
        return self.current_token 
    
    def intVal(self):
        return self.current_token
    
    def stringVal(self):
        return self.current_token[1:-1] # remove "
    
