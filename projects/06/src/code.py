import json

class Code:
    def __init__(self):
        json_data = json.load(open("./binary_config.json","r"))
        self.destDict = json_data["dest"]
        self.compDict = json_data["comp"]
        self.jumpDict = json_data["jump"]
        
    def dest2bin(self, str_dest):
        return self.destDict[str_dest]
    def comp2bin(self, str_comp):
        return self.compDict[str_comp]
    def jump2bin(self, str_jump):
        return self.jumpDict[str_jump]

        