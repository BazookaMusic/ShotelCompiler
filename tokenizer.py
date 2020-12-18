from scannerGenerator import Tokens
import subprocess
from enum import Enum

# Conversion from token to enum
TokenType = Enum("TokenType", Tokens)

class Token:
    '''A token object'''
    def __init__(self,text):
        self.type = self.value = None
        self.parse(text)
    
    def parse(self,text: str):
        paren = text.find("(")

        if paren == -1:
            self.type = TokenType[text]
            self.value = None
        else:
            self.type = TokenType[text[0:paren]]
            value = text[paren + 1:-1]
            self.value = int(value) if self.type == TokenType.INT else value
    
    def __repr__(self):
        value = "(" + str(self.value) + ")" if self.value is not None else ''
        return f"{self.type}{value}"

class TokenConverter:
    '''A class to convert a list of lines into compiler tokens.'''
    def __init__(self, tokenLines):
        self.tokens = list(map(lambda tokenText: Token(tokenText), tokenLines))
    
    


