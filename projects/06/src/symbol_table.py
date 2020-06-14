import json
class SymbolTable:
    def __init__(self,):
        json_data = json.load(open("./binary_config.json","r"))
        self.table = {}
        self.table.update(json_data["define_symbol"])

    def addEntry(self,symbol,address):
        self.table[symbol] = address
    
    def contains(self,symbol):
        return symbol in self.table.keys()

    def getAddress(self,symbol):
        return self.table[symbol]