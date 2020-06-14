import re
from jackTokenizer import JackTokenizer
import json
class CompilationEngine:
    def __init__(self, input_filename):
        self.tokenizer = JackTokenizer(input_filename)
        self.xml_code = []
        self.num_indent = 0
        self.compileClass()
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
        self.compileIdentifier()
        self.compileSymbol()
        while self.tokenizer.current_token in ['static', 'field'] :
            self.compileClassVarDec()   
        
        while self.tokenizer.current_token in ['constructor', 'function','method']:
            self.compileSubroutine()
        self.compileSymbol(True)
        self.writeEndStatement('class')

    def compileType(self):
        if self.tokenizer.current_token in ['int','char','boolean']:
            self.compileKeyword()
        else: self.compileIdentifier()

    def compileClassVarDec(self): 
        self.writeStartStatement('classVarDec')
        self.compileKeyword() 
        self.compileType()
        self.compileIdentifier()
        while self.tokenizer.current_token == ',': # many define variable
            self.compileSymbol()
            self.compileIdentifier()
        
        self.compileSymbol()
        self.writeEndStatement('classVarDec') 

    def compileSubroutine(self):
        self.writeStartStatement('subroutineDec')
        self.compileKeyword()
        if self.tokenizer.current_token == 'void':
            self.compileKeyword()
        else: self.compileType()

        self.compileIdentifier()
        self.compileSymbol()
        self.compileParameterList()
        self.compileSymbol()
        self.compileSubroutineBody()
        self.writeEndStatement('subroutineDec')

    def compileParameterList(self):
        self.writeStartStatement('parameterList')
        if self.tokenizer.current_token in  ['int','char','boolean'] or self.tokenizer.tokenType() == 'IDENTIFIER':
            self.compileType()
            self.compileIdentifier()

            while self.tokenizer.current_token == ',':
                self.compileSymbol()
                self.compileType()
                self.compileIdentifier()
        self.writeEndStatement('parameterList')

    def compileSubroutineBody(self):
        self.writeStartStatement('subroutineBody')
        self.compileSymbol()
        while self.tokenizer.current_token == 'var':
            self.compileVarDec()
        
        self.compileStatements()
        self.compileSymbol()
        self.writeEndStatement('subroutineBody')

    def compileVarDec(self):
        self.writeStartStatement('varDec')
        self.compileKeyword()
        self.compileType()
        self.compileIdentifier()
        while self.tokenizer.current_token == ',':
            self.compileSymbol()
            self.compileIdentifier()
        
        self.compileSymbol()
        self.writeEndStatement('varDec')
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
        self.writeEndStatement('doStatement')

    def compileLet(self):
        self.writeStartStatement('letStatement')
        self.compileKeyword()
        self.compileIdentifier()
        if self.tokenizer.current_token == '[':
            self.compileSymbol()
            self.compileExpression()
            self.compileSymbol()
        self.compileSymbol()
        self.compileExpression()
        self.compileSymbol()
        self.writeEndStatement('letStatement')

    def compileWhile(self):

        self.writeStartStatement('whileStatement')
        self.compileKeyword()
        self.compileSymbol()
        self.compileExpression()
        self.compileSymbol()
        self.compileSymbol()
        self.compileStatements()
        self.compileSymbol()
        self.writeEndStatement('whileStatement')

    def compileReturn(self):
        self.writeStartStatement('returnStatement')
        self.compileKeyword()
        if self.tokenizer.current_token != ';':
            self.compileExpression()
        self.compileSymbol()
        self.writeEndStatement('returnStatement')

    def compileIf(self):
        self.writeStartStatement('ifStatement')
        self.compileKeyword()
        self.compileSymbol()
        self.compileExpression()
        self.compileSymbol()
        self.compileSymbol()
        self.compileStatements()
        self.compileSymbol()
        if self.tokenizer.current_token == 'else':
            self.compileKeyword()
            self.compileSymbol()
            self.compileStatements()
            self.compileSymbol()

        self.writeEndStatement('ifStatement')

    def compileSubroutineCall(self,is_term=False):
        if not is_term: 
            self.compileIdentifier()

        if self.tokenizer.current_token == '.':
            self.compileSymbol()
            self.compileIdentifier()
        self.compileSymbol()
        self.compileExpressionList()
        self.compileSymbol()

    def compileExpressionList(self):
        self.writeStartStatement('expressionList')
        if self.tokenizer.current_token != ')': # if argument exist, ex. func(a,b)
            self.compileExpression()
            while self.tokenizer.current_token == ',': 
                self.compileSymbol()
                self.compileExpression()
        self.writeEndStatement('expressionList')

    def compileExpression(self):
        self.writeStartStatement('expression')
        self.compileTerm()
        while self.tokenizer.current_token in ['-','+','=','<','>','/','&','|','*']:
            self.compileSymbol()
            self.compileTerm()
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
            self.compileIntegerConstant()
        elif self.tokenizer.tokenType() == 'STRING_CONST':
            self.compileStringConstant()
        elif self.tokenizer.current_token in ['true','false','null','this']:
            self.compileKeyword()
        elif self.tokenizer.tokenType() == 'IDENTIFIER' :
            self.compileIdentifier() # varName or subroutineName
            if self.tokenizer.current_token == '[': # varName[]
                self.compileSymbol()
                self.compileExpression()
                self.compileSymbol()
            elif self.tokenizer.current_token == '(' or self.tokenizer.current_token == '.': # subroutineCall
                self.compileSubroutineCall(is_term=True) # already called compileIdentifier(), is_term = True

        elif self.tokenizer.current_token == '(': 
            self.compileSymbol()
            self.compileExpression()
            self.compileSymbol()
        elif self.tokenizer.current_token in ['~','-']:
            self.compileSymbol()
            self.compileTerm()
        self.writeEndStatement('term')




