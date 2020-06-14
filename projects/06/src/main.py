from parser import Parser
from code import Code
from symbol_table import SymbolTable
import sys
import re

def register_symble(parser,symbol_table):
    rom_address = 0
    while parser.hasMoreCommands():
        parser.advance()
        cmdtype = parser.commandType()
        if cmdtype == "A_COMMAND" or cmdtype == "C_COMMAND":
            rom_address += 1
        elif cmdtype == "L_COMMAND" :
            symbol = parser.symbol()
            if not symbol_table.contains(symbol):
                symbol_table.addEntry(symbol,format(rom_address, '04x'))

def save_hack(file_path,binary_code):
    with open(file_path,"w") as f:
        for b in binary_code:
            f.writelines(b+"\n")


if __name__=="__main__":

    path = sys.argv[1]
    code = Code()
    parser = Parser(path+".asm")
    symbol_table=SymbolTable()
    binary_code = []
    ram_address=16
    flag=0
    
    register_symble(parser,symbol_table)
    parser.reset_idx()
    
    while parser.hasMoreCommands():

        parser.advance()
        cmdtype = parser.commandType()
        if cmdtype == "A_COMMAND":
            symbol = parser.symbol()
            if re.search("[A-Za-z]",symbol) != None:
                if symbol_table.contains(symbol):
                    address = symbol_table.getAddress(symbol)#16進数
                else: 
                    address = format(ram_address, '04x') #16進数
                    symbol_table.addEntry(symbol,address)
                    ram_address += 1

                symbol=int(address,16)

            binary = bin(int(symbol))[2:]
            bit16 = ("0"*(16-len(binary)))+ binary 

        elif cmdtype == "C_COMMAND":
            dest_bin = code.dest2bin(parser.dest())
            comp_bin = code.comp2bin(parser.comp())
            jump_bin = code.jump2bin(parser.jump())
            bit16 = "111"+comp_bin+dest_bin+jump_bin

        else: continue # L_COMMAND((Xxx))はバイナリコードへ変換した際に削除される形式なので飛ばす
        
        binary_code.append(bit16)


    save_hack(path+".hack",binary_code)
        






