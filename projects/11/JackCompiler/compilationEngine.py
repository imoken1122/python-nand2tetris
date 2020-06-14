import re
from jackTokenizer import JackTokenizer
from vmWriter import VMWriter
from symbolTable import SymbolTable
import json
class CompilationEngine:
    def __init__(self, input_filename):
        self.filename = input_filename
        self.tokenizer = JackTokenizer(input_filename)
        self.xml_code = []
        self.num_indent = 0
        self.nLables = 0
        self.classname = None
        self.vmWriter = VMWriter()
        self.symboltable = SymbolTable()
        self.compileClass()

    def symbolRegister(self,kind = None,type = None):
        name = self.tokenizer.identifier()
        self.symboltable.define(name,type,kind)

    def writeStatement(self,tag,xxx):
        indent = '\t'* self.num_indent
        self.xml_code.append(f'{indent}<{tag}> {xxx} </{tag}>')
    def writeStartStatement(self,tag):
        indent='\t' * self.num_indent
        self.xml_code.append(f'{indent}<{tag}>')
        self.num_indent +=1 

    def writeEndStatement(self,tag):
        self.num_indent -= 1
        indent='\t'* self.num_indent
        self.xml_code.append(f'{indent}</{tag}>')

    def compileKeyword(self):
        token = self.tokenizer.keyword()
        self.writeStatement('keyword', token)
        self.tokenizer.advance()
        
    def compileIdentifier(self):
        token = self.tokenizer.identifier()
        self.writeStatement('identifier', token)
        self.tokenizer.advance() 

    def compileSymbol(self,class_finish=False):
        token = self.tokenizer.symbol()
        if token == '<':
            token = '&lt;'
        elif token == '>':
            token = '&gt;'
        elif token == '&':
            token = '&amp;'

        self.writeStatement('symbol', token)
        if not class_finish:
            self.tokenizer.advance()

    def compileClass(self):
        self.writeStartStatement('class') 
        self.compileKeyword()
        self.classname = self.tokenizer.current_token
        self.compileIdentifier()
        self.compileSymbol()
        n = 0
        while self.tokenizer.current_token in ['static', 'field'] :
            self.compileClassVarDec()   

        while self.tokenizer.current_token in ['constructor', 'function','method']:
            n +=1
            self.compileSubroutine()
            #if n == 1: break


        self.compileSymbol(True)
        self.writeEndStatement('class')

    def compileType(self):
        if self.tokenizer.current_token in ['int','char','boolean']:
            self.compileKeyword()
        else: self.compileIdentifier()

    def compileClassVarDec(self): # var int c = xxx; 
        self.writeStartStatement('classVarDec')
        kind = self.tokenizer.current_token
        self.compileKeyword() 
        type  = self.tokenizer.current_token
        self.compileType()
        self.symbolRegister(kind, type)
        self.compileIdentifier()
        while self.tokenizer.current_token == ',': # many define variable
            self.compileSymbol()
            self.symbolRegister(kind,type)
            self.compileIdentifier()
        
        self.compileSymbol()
        self.writeEndStatement('classVarDec') 

    def compileSubroutine(self):
        self.symboltable.startSubroutine()
        self.writeStartStatement('subroutineDec')

        kind = self.tokenizer.current_token
        if kind == 'method':
            self.symboltable.define('this',self.classname, 'argument' )
        self.compileKeyword()
        if self.tokenizer.current_token == 'void':
            self.compileKeyword()
        else: self.compileType()

        functionname = self.tokenizer.current_token
        functionname = f'{self.classname}.{functionname}'
        self.compileIdentifier() # funcname
        self.compileSymbol() # (
        self.compileParameterList() # parma1,param2,...
        self.compileSymbol() #)
        self.compileSubroutineBody(functionname,kind) # { statements }

        
        self.writeEndStatement('subroutineDec')

    def compileParameterList(self):
        self.writeStartStatement('parameterList')
        if self.tokenizer.current_token in  ['int','char','boolean'] or self.tokenizer.tokenType() == 'IDENTIFIER':
            type = self.tokenizer.current_token
            self.compileType()
            self.symbolRegister(type = type,kind='argument')
            self.compileIdentifier()

            while self.tokenizer.current_token == ',':
                self.compileSymbol()
                type = self.tokenizer.current_token
                self.compileType()
                self.symbolRegister(type = type,kind='argument')
                self.compileIdentifier()
        self.writeEndStatement('parameterList')

    def compileSubroutineBody(self,functionname, kind):
        self.nLocals = 0
        idx = -1
        self.writeStartStatement('subroutineBody')
        self.compileSymbol()
        self.vmWriter.writeFunction(functionname,self.nLocals)

        if kind =='constructor':
            self.vmWriter.writePush('constant',self.symboltable.varCount('field') )
            self.vmWriter.writeCall('Memory.alloc',1)
            self.vmWriter.writePop('pointer',0)
            idx = -4
        elif kind == 'method' :
            self.vmWriter.writePush('argument',0)
            self.vmWriter.writePop('pointer',0)
            idx=-3
        while self.tokenizer.current_token == 'var':
            self.nLocals += self.compileVarDec()

        self.vmWriter.vm_code[idx]=f'function {functionname} {self.nLocals}'

        self.compileStatements()

        self.compileSymbol()
        self.writeEndStatement('subroutineBody')

    def compileVarDec(self):
        nVar = 1
        self.writeStartStatement('varDec')
        self.compileKeyword()
        type = self.tokenizer.current_token
        self.compileType()
        self.symbolRegister(kind='var',type =type )
        self.compileIdentifier()

        while self.tokenizer.current_token == ',':
            nVar +=1
            self.compileSymbol()
            self.symbolRegister(kind = 'var',type=type )
            self.compileIdentifier()
        self.compileSymbol()
        self.writeEndStatement('varDec')
        return nVar

    def compileStatements(self):
        self.writeStartStatement('statements')
        while self.tokenizer.current_token in ['let','if','while','do','return']:
            
            self.compileStatement()
            
        self.writeEndStatement('statements' )
    def compileStatement(self) :
        if self.tokenizer.current_token == 'let':
            self.compileLet()
        elif self.tokenizer.current_token =='if':

            self.compileIf()
        elif self.tokenizer.current_token =='while':
            self.compileWhile()
        elif self.tokenizer.current_token == 'do':
            self.comppileDo()
        elif self.tokenizer.current_token == 'return':
            self.compileReturn()
    def comppileDo(self):
        self.writeStartStatement('doStatement')
        self.compileKeyword()
        self.compileSubroutineCall()
        self.compileSymbol()
        self.vmWriter.writePop('temp',0) #戻り値を保存
        self.writeEndStatement('doStatement')

    def compileLet(self):
        self.writeStartStatement('letStatement')
        self.compileKeyword()
        name = self.tokenizer.current_token
        kind = self.symboltable.kindOf(name)
        index = self.symboltable.indexOf(name)

        self.compileIdentifier() #varName

        if self.tokenizer.current_token == '[': #varName[]
            self.compileSymbol()
            self.compileExpression() # [n]
            self.compileSymbol()
            if kind == 'static':
                self.vmWriter.writePush('static',index)
            elif kind == 'field':
                self.vmWriter.writePush('this',index) # vm言語でのfieldはthis
            elif kind == 'argument':
                self.vmWriter.writePush('argument',index)
            elif kind == 'var':
                self.vmWriter.writePush('local',index) #vm言語でのvarはlocal

            self.vmWriter.writeArithmetic('add') # 配列varNameのベースアドレス + n 

            self.compileSymbol() # =
            self.compileExpression()
            self.vmWriter.writePop('temp',0)
            self.vmWriter.writePop('pointer',1)
            self.vmWriter.writePush('temp',0)

            self.vmWriter.writePop('that',0) #var[n] = expression


            """
            なぜか上のように一度 temp に逃さないとエラーになる
            self.vmWriter.writePop('pointer',1) #that
            self.compileSymbol() # =
            self.compileExpression()
        
            self.vmWriter.writePop('that',0) #var[n] = expression
            """
        else: # varName 
            
            self.compileSymbol()
            
            self.compileExpression() # 代入する値をpush
            if kind == 'static':
                self.vmWriter.writePop('static',index)
            elif kind == 'field':
                self.vmWriter.writePop('this',index) # vm言語でのfieldはthis
            elif kind == 'argument':
                self.vmWriter.writePop('argument',index)
            elif kind == 'var':
                self.vmWriter.writePop('local',index) #vm言語でのvarはlocal 

        
        self.compileSymbol()

        self.writeEndStatement('letStatement')

    def compileWhile(self):
        true_label = f'WHILE_True_{self.nLables}'
        false_label = f'WHILE_False_{self.nLables}'
        self.nLables += 1

        self.writeStartStatement('whileStatement')
        self.compileKeyword()
        self.vmWriter.writeLable(true_label)
        self.compileSymbol()
        self.compileExpression() # cond
        self.vmWriter.writeArithmetic('not') # ~cond 
        self.vmWriter.writeIf(false_label) 
        self.compileSymbol()
        self.compileSymbol()
        self.compileStatements()
        self.compileSymbol()
        self.vmWriter.writeGoto(true_label)
        self.vmWriter.writeLable(false_label)
        self.writeEndStatement('whileStatement')

    def compileReturn(self):
        self.writeStartStatement('returnStatement')
        self.compileKeyword()
        if self.tokenizer.current_token != ';':
            self.compileExpression()
        else:
            self.vmWriter.writePush('constant',0)

        self.compileSymbol()
        self.vmWriter.writeReturn()
        self.writeEndStatement('returnStatement')

    def compileIf(self):
        true_label = f'IF_True_{self.nLables}'
        false_label = f'IF_False_{self.nLables}'
        self.nLables += 1

        self.writeStartStatement('ifStatement')
        self.compileKeyword()
        self.compileSymbol()
        self.compileExpression()
        self.vmWriter.writeArithmetic('not') # ~cond 
        self.vmWriter.writeIf(false_label)
        self.compileSymbol()
        self.compileSymbol()
        self.compileStatements()
        self.compileSymbol()
        self.vmWriter.writeGoto(true_label)

        self.vmWriter.writeLable(false_label)
        if self.tokenizer.current_token == 'else':
            self.compileKeyword()
            self.compileSymbol()
            self.compileStatements()
            self.compileSymbol()

        self.vmWriter.writeLable(true_label)
        self.writeEndStatement('ifStatement')

    def compileSubroutineCall(self,is_term=False):

        name = self.tokenizer.current_token #varName or className or subroutineName
        kind = self.symboltable.kindOf(name)

        nArgs = 0
        if kind != None:  # varName.subroutine
            nArgs += 1 # push
            index = self.symboltable.indexOf(name)
            if kind == 'static':
                self.vmWriter.writePush('static',index)
            elif kind == 'field':
                self.vmWriter.writePush('this',index) # vm言語でのfieldはthis
            elif kind == 'argument':
                self.vmWriter.writePush('argument',index)
            elif kind == 'var':
                self.vmWriter.writePush('local',index) #vm言語でのvarはlocal

            if not is_term:
                self.compileIdentifier() # varName

            self.compileSymbol()

            type =  self.symboltable.typeOf(name)
            name = f'{type}.{self.tokenizer.current_token}' 
            
            self.compileIdentifier() #subroutineName
        else: 

            if not is_term: 
                self.compileIdentifier() #className or subroutineName

            if self.tokenizer.current_token == '.': # className.subroutine
                self.compileSymbol()
                name = f'{name}.{self.tokenizer.current_token}'
                self.compileIdentifier() #subroutineName
            else: #subroutine
                self.vmWriter.writePush('pointer',0)
                name = f'{self.classname}.{name}'
                nArgs += 1 # push
            
        self.compileSymbol()
        
        nArgs += self.compileExpressionList()
        self.compileSymbol()
        
        self.vmWriter.writeCall(name,nArgs)

    def compileExpressionList(self):
        nArgs = 0
        self.writeStartStatement('expressionList')
        if self.tokenizer.current_token != ')': # if argument exist, ex. func(a,b)
            self.compileExpression()
            nArgs += 1 # push
            while self.tokenizer.current_token == ',': 
                self.compileSymbol()
                self.compileExpression()
                nArgs += 1 # push
        self.writeEndStatement('expressionList')
        return nArgs

    def compileExpression(self):
        self.writeStartStatement('expression')
        self.compileTerm()
        while self.tokenizer.current_token in ['-','+','=','<','>','/','&','|','*']:
            symbol = self.tokenizer.current_token
            self.compileSymbol()
            self.compileTerm()

            if symbol == '+':
                self.vmWriter.writeArithmetic('add')
            elif symbol == '-':
                self.vmWriter.writeArithmetic('sub')
            elif symbol =='*':
                self.vmWriter.writeCall('Math.multiply',2)
            elif symbol =='/':
                self.vmWriter.writeCall('Math.divide',2)
            elif symbol == '|':
                self.vmWriter.writeArithmetic('or')
            elif symbol == '&':
                self.vmWriter.writeArithmetic('and')
            elif symbol == '<':
                self.vmWriter.writeArithmetic('lt')
            elif symbol == '>':
                self.vmWriter.writeArithmetic('gt')
            elif symbol == '=':
                self.vmWriter.writeArithmetic('eq')

        self.writeEndStatement('expression') 

    def compileIntegerConstant(self) :
        self.writeStatement('integerConstant',self.tokenizer.intVal())
        self.tokenizer.advance()

    def compileStringConstant(self) :
        self.writeStatement('stringConstant',self.tokenizer.stringVal())
        self.tokenizer.advance()

    def compileTerm(self):
        self.writeStartStatement('term')
        
        if self.tokenizer.tokenType() == 'INT_CONST':
            self.vmWriter.writePush('constant',self.tokenizer.current_token)
            self.compileIntegerConstant()
        elif self.tokenizer.tokenType() == 'STRING_CONST':
            string = self.tokenizer.stringVal()
            self.vmWriter.writePush('constant',len(string))
            self.vmWriter.writeCall('String.new',1)
            for s in string:
                self.vmWriter.writePush('constant',ord(s))
                self.vmWriter.writeCall('String.appendChar',2)
            self.compileStringConstant()

        elif self.tokenizer.current_token in ['true','false','null','this']:
            token = self.tokenizer.current_token
            if token == 'true':
                self.vmWriter.writePush('constant',1)
                self.vmWriter.writeArithmetic('neg')
            elif token == 'false':
                self.vmWriter.writePush('constant',0)
            elif token == 'null':
                self.vmWriter.writePush('constant',0)
            elif token == 'this':
                self.vmWriter.writePush('pointer',0)

            self.compileKeyword()

        elif self.tokenizer.tokenType() == 'IDENTIFIER' :
            name = self.tokenizer.current_token #varName
            
            kind = self.symboltable.kindOf(name) 
            is_term = False
            if kind!= None:
                index = self.symboltable.indexOf(name)
                if kind == 'static':
                    self.vmWriter.writePush('static',index)
                    self.compileKeyword()
                elif kind == 'field':
                    self.vmWriter.writePush('this',index) # vm言語でのfieldはthis
                    self.compileKeyword()
                elif kind == 'argument':
                    self.vmWriter.writePush('argument',index)
                    self.compileKeyword()
                elif kind == 'var':
                    self.vmWriter.writePush('local',index) #vm言語でのvarはlocal
                    self.compileKeyword()
            else:
                self.compileIdentifier() # varName or subroutineName
                is_term = True
            # 怪しいここは
            if self.tokenizer.current_token == '[': # varName[]
                self.compileSymbol()
                self.compileExpression() # [n]
                self.compileSymbol()
                self.vmWriter.writeArithmetic('add') #base_addr + n
                self.vmWriter.writePop('pointer',1)
                self.vmWriter.writePush('that',0)
            elif self.tokenizer.current_token == '(': #subroutine()
                self.compileSymbol()
                nArgs = self.compileExpressionList()
                self.compileSymbol()
                self.vmWriter.writeCall(name,nArgs)
            elif self.tokenizer.current_token == '.': # subroutine.
                self.compileSymbol()
                nArgs = 0
                
                if kind != None:
                    name = self.symboltable.typeOf(name)
                    nArgs = 1
                name = f'{name}.{self.tokenizer.current_token}'
                self.compileIdentifier()
                self.compileSymbol()
                nArgs += self.compileExpressionList()
                self.compileSymbol()
                
                self.vmWriter.writeCall(name,nArgs)

        elif self.tokenizer.current_token == '(': 
            self.compileSymbol()
            self.compileExpression()
            self.compileSymbol()

        elif self.tokenizer.current_token == '-':
            self.compileSymbol()
            self.compileTerm()
            self.vmWriter.writeArithmetic('neg')

        elif self.tokenizer.current_token== '~':
            self.compileSymbol()
            self.compileTerm()
            self.vmWriter.writeArithmetic('not')

       
        self.writeEndStatement('term')




