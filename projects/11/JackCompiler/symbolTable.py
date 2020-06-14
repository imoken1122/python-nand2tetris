class SymbolTable:
    def __init__(self):
        #{'static': {'name1':[],'name2':[],'name3':[],....}}
        self.symbol_table ={'static':{}, 'field':{}, 'argument':{},'var':{}}

    def startSubroutine(self,):
        self.symbol_table['argument'] = {}
        self.symbol_table['var'] = {}

    def define(self, name,type,kind):
        self.symbol_table[kind][name] = [kind,type,self.varCount(kind)]

    def varCount(self,kind):
        return len(self.symbol_table[kind].keys())

    def kindOf(self,name):
        
        if name in self.symbol_table['static'].keys():
            return self.symbol_table['static'][name][0]
        elif name in self.symbol_table['field'].keys():
            return self.symbol_table['field'][name][0]
        elif name in self.symbol_table['argument'].keys():
            return self.symbol_table['argument'][name][0]
        elif name in self.symbol_table['var'].keys():
            return self.symbol_table['var'][name][0]
        else: return None

    def typeOf(self,name):
        if name in self.symbol_table['static'].keys():
            return self.symbol_table['static'][name][1]
        elif name in self.symbol_table['field'].keys():
            return self.symbol_table['field'][name][1]
        elif name in self.symbol_table['argument'].keys():
            return self.symbol_table['argument'][name][1]
        elif name in self.symbol_table['var'].keys():
            return self.symbol_table['var'][name][1]
        else:return None

    def indexOf(self, name):
        if name in self.symbol_table['static'].keys():
            return self.symbol_table['static'][name][2]
        elif name in self.symbol_table['field'].keys():
            return self.symbol_table['field'][name][2]
        elif name in self.symbol_table['argument'].keys():
            return self.symbol_table['argument'][name][2]
        elif name in self.symbol_table['var'].keys():
            return self.symbol_table['var'][name][2]
        else: return None