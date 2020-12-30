#!/usr/bin/python3
from collections import deque
from enum import Enum
from tokenizer import Token, TokenType
import parser_helper
from queue import Queue
from shotel_ast import *

class InvalidEOFError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

class TokensNotExhaustedError(Exception):
    pass

class Parser:
    '''
    The parser class, a recursive descent parser implementation.
    See language.bnf, class merely implements the bnf grammar.
    '''
    def __init__(self, tokens):
        self.tokens: ['Enum'] = tokens
        self.stack = deque(tokens)
    
    def GetToken(self):
        token = self.stack[0]
        self.stack.popleft()

        return token
    
    def Program(self):
        self.Program = Program(self.Definitions())

        if len(self.stack) > 0:
            raise TokensNotExhaustedError(f"Parsing completed but EOF not reached. Remaining tokens:{list(self.stack)}")
        
        return self.Program
    
    def Definitions(self):
        definitions = []
        while (True):
            definition = self.Definition()

            if definition is None:
                return definitions
            
            definitions.append(definition)
        
    def Definition(self):
        if len(self.stack) == 0:
            return None
        
        top: Token = self.GetToken()

        if top.type == TokenType.FN:
            return self.Fn()
        elif top.type == TokenType.TYPE:
            return self.Type()
    
    # TYPE
    
    def Type(self):
        self.EOFCheck("Expected name of type but got EOF.")

        name: Token = self.GetToken()

        if name.type != TokenType.UID:
            raise InvalidTokenError(f"Expected UID for Type name but got {name.type} instead")

        self.AssertExistence(TokenType.ASSIGN)

        constructors: ['Constructor'] = self.Constructors(upperCaseParams=True)

        return TypeDefinition(name.value, constructors)
    
    def Constructors(self, upperCaseParams = False):
        self.EOFCheck("Expected list of constructors and got none instead.")

        constructors: ['Constructor'] = []

        while True:
            constructor = self.Constructor(upperCaseParams)

            constructors.append(constructor)

            # no more tokens, end of constructors
            if len(self.stack) == 0:
                return constructors

            # at least one, is it a comma
            nextToken: Token = self.stack[0]
            
            if nextToken.type == TokenType.COMMA:
                self.GetToken()
                continue

            break

        return constructors
    
    def Constructor(self, upperCaseParams = False):
        self.EOFCheck("Expected constructor but got EOF instead.")

        name = self.GetToken()

        if name.type != TokenType.UID:
            raise InvalidTokenError(f"Invalid constructor definition {name.value}." + 
        "Constructor names should start with a capital letter." if name.type == TokenType.LID else f"Expected constructor name but got {name.type} instead.")
        
        return Constructor(name.value, self.Params(upperCaseParams))
    
    # FN

    def Fn(self):
        self.EOFCheck("Expected function definition but got EOF instead.")

        name = self.GetToken()

        if name.type != TokenType.UID:
            raise InvalidTokenError(f"Expected uppercase function name but got {name.type} instead.")

        params = self.Params()

        self.AssertExistence(TokenType.OCURLY)

        body = self.Expression()

        self.AssertExistence(TokenType.CCURLY)

        return FnDefinition(name.value, params, body)

    
    def Expression(self):
        return self.Comparison()
    
    def Comparison(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        left = self.Add()

        nextToken = self.Peek()

        node = None

        if nextToken.type == TokenType.EQUAL:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.EQUALS, left, self.Comparison())
        elif nextToken.type == TokenType.NEQUAL:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.NEQUALS, left, self.Comparison())
        else:
            node = left

        return node
    
    def Add(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        left = self.Mul()

        nextToken = self.Peek()

        node = None

        if nextToken.type == TokenType.PLUS:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.PLUS, left, self.Add())
        elif nextToken.type == TokenType.MINUS:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.MINUS, left, self.Add())
        elif nextToken.type == TokenType.RSHIFT:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.RSHIFT, left, self.Add())
        elif nextToken.type == TokenType.LSHIFT:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.LSHIFT, left, self.Add())
        else:
            node = left

        return node
    
    def Mul(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        left = self.Or()

        nextToken = self.Peek()

        node = None

        if nextToken.type == TokenType.TIMES:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.TIMES, left, self.Mul())
        elif nextToken.type == TokenType.DIVIDE:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.DIVIDE, left, self.Mul())
        elif nextToken.type == TokenType.MODULO:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.MODULO, left, self.Mul())
        else:
            node = left

        return node
    
    
    def Or(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        left = self.And()

        nextToken = self.Peek()

        node = None

        if nextToken.type == TokenType.OR:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.OR, left, self.Or())
        else:
            node = left

        return node
    
    def And(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        left = self.MaybeNotApplication()

        nextToken = self.Peek()

        node = None

        if nextToken.type == TokenType.AND:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.AND, left, self.And())
        elif nextToken.type == TokenType.XOR:
            self.GetToken()
            node = BinaryOperation(BinaryOperation.BinaryOperationKind.XOR, left, self.And())
        else:
            node = left
        
        return node
    
    def MaybeNotApplication(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        if self.Peek().type == TokenType.NOT:
            self.GetToken()
            return UnaryOperation(UnaryOperation.UnaryOperationKind.NOT, self.Application())
        
        return self.Application()
    
    
    def Application(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        applications = None

        # the tree of applications is built in reverse,
        # because we want right to left application
        # but parsing is done left to right

        # get first application
        application = self.ApplicationBase()

        # check if there's a second application, maybe we don't need to allocate a node
        if self.ApplicationExists():
            current_application_node = FunctionApplication(application, self.ApplicationBase())
        else:
            return application

        # for the rest, build the tree in reverse, return the root
        while self.ApplicationExists():
            current_application_node = FunctionApplication(current_application_node, self.ApplicationBase())
        
        return current_application_node

    def ApplicationExists(self):
        if len(self.stack) == 0:
            return False
        
        nextTokenType = self.stack[0].type

        return nextTokenType in [TokenType.INT, TokenType.LID, TokenType.UID, TokenType.LITERAL,
        TokenType.OPAR, TokenType.CASE]

    def ApplicationBase(self):
        self.EOFCheck("Expected expression but got EOF instead.")

        nextToken = self.GetToken()

        if nextToken.type == TokenType.INT:
            return IntNode(nextToken.value)
        elif nextToken.type == TokenType.LITERAL:
            return StringNode(nextToken.value)
        elif nextToken.type == TokenType.LID:
            return LID(nextToken.value)
        elif nextToken.type == TokenType.UID:
            return UID(nextToken.value)
        elif nextToken.type == TokenType.CASE:
            return self.Case()
        elif nextToken.type == TokenType.OPAR:
            expression = self.Comparison()

            self.AssertExistence(TokenType.CPAR)

            return expression
        else:
            raise InvalidTokenError(f"Expectied a function or a value but got {self.Peek()} instead.")

    def Case(self):
        self.EOFCheck("Expected Case statement but got EOF instead.")

        expression = self.Comparison()

        branches = self.Branches()
        return CaseOf(expression, branches)
    
    def Branches(self):
        self.EOFCheck("Expected branches but got EOF instead.")

        branches: ['Branch'] = []

        nextExists = True

        while nextExists:
            branches.append(self.Branch())
            nextExists = self.BranchExists()
        
        return branches
    
    def BranchExists(self):
        return len(self.stack) > 0 and self.stack[0].type == TokenType.PATTERN
    
    def Branch(self):
        self.EOFCheck("Expected branch but got EOF instead.")

        # remove pattern dash
        self.AssertExistence(TokenType.PATTERN)

        pattern = self.Pattern()

        self.AssertExistence(TokenType.ARROW)

        self.AssertExistence(TokenType.OCURLY)

        expression = self.Comparison()

        self.AssertExistence(TokenType.CCURLY)

        return Branch(pattern, expression)

    def Pattern(self):
        self.EOFCheck("Expected pattern variable or constructor but got EOF instead.")

        if self.Peek().type == TokenType.LID:
            varname = self.GetToken().value
            return PatternVar(varname)
        else:
            constructor = self.Constructor(upperCaseParams=False)
            return PatternConstructor(constructor.name, constructor.types)
    
    # Get lowercase params
    
    def Params(self, upperCaseParams = False):
        params: [str] = []
        
        case = TokenType.UID if upperCaseParams else TokenType.LID
        next_exists = len(self.stack) != 0 and self.Peek().type == case
        while next_exists:
            param = self.Param(upperCaseParams)
            params.append(param)

            next_exists = len(self.stack) != 0 and self.Peek().type == case
        
        return params

    def Param(self, upperCase = False):
        self.EOFCheck("Expected constructor lowercase parameter but got EOF instead.")

        param = self.GetToken()

        typeOfToken = TokenType.UID if upperCase else TokenType.LID 

        if param.type != typeOfToken:
            case = "lowercase" if not upperCase else "uppercase"
            raise InvalidTokenError(f"Expected {case} constructor param but got {param.type} instead.")

        return param.value
    
    def ConsumeToken(self):
        self.GetToken()

    # helpers
    
    def EOFCheck(self, message):
        if len(self.stack) == 0:
            raise InvalidEOFError(message)
    
    def AssertExistence(self, tokenType: 'Enum'):
        self.EOFCheck(f"Expected token of type {tokenType} but got EOF instead")

        nextToken = self.GetToken()
        if nextToken.type != tokenType:
            raise InvalidTokenError(f"Expected token of type {tokenType} but got {nextToken.type} instead.")
    
    def Peek(self, at_least_n_tokens = 1):
        if len(self.stack) < at_least_n_tokens:
            raise InvalidEOFError(f"Expected at least {at_least_n_tokens} tokens but stack contained {len(self.stack)}.")

        return self.stack[0]
    
    def TreeToString(body):
        if body is None:
            return ""
        
        result = str(body)
        if isinstance(body, BinaryOperation):
            return result + " " + Parser.TreeToString(body.left) + " " + Parser.TreeToString(body.right)
        elif isinstance(body, UnaryOperation):
            return result + " " +Parser.TreeToString(body.op)
        else:
            return result



