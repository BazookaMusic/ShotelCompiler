#!/usr/bin/python3
Tokens = [
    "PLUS",
    "MINUS",
    "DIVIDE",
    "TIMES",
    "MODULO",
    "LSHIFT",
    "RSHIFT",
    "AND",
    "OR",
    "XOR",
    "NOT",
    "INT",
    "FN",
    "TYPE",
    "CASE",
    "PATTERN",
    "OCURLY",
    "CCURLY",
    "OPAR",
    "CPAR",
    "COMMA",
    "ARROW",
    "ASSIGN",
    "EQUAL",
    "NEQUAL",
    "LID",
    "UID",
    "LITERAL"
]

Patterns = [
        r"[ \n]+",
        "\+ ",
        "-",
        "\/",
        "\* ",
        "\% ",
        "\<\< ",
        "\>\> ",
        "and ",
        "or ",
        "xor ",
        "\! ",
        "[0-9]+ ",
        "fn ",
        "type ",
        "case ",
        "\|",
        "\{",
        "\} ",
        "\( ",
        "\) ",
        ",  ",
        "=>",
        "=",
        "==",
        "!=",
        "[a-z][a-zA-Z]*",
        "[A-Z][a-zA-Z]* ",
        r"\"(([^\"]|\\\")*[^\\])?\" "
        ]

class ScannerGenerator:
    def __init__(self):
        pass

    def TokenPrint(self,token):
        if token == "INT" or token == "LITERAL" or token == "LID" or token == "UID":
            return '\"{0}\" << "(" << yytext << ")"'.format(token)
        else:
            return '"' + token + '"'
    
    def generate(self):
        header = '''
%option noyywrap
%{
#include <iostream>
#include <stdio.h>

%}

%%
'''
        whitespace = [Patterns[0] + " {}"];
        matchings = ['{0} {2} std::cout << {1} << std::endl; {3}'.format(pattern, self.TokenPrint(token), "{", "}") for token,pattern in zip(Tokens, Patterns[1:])]

        flex_patters = "\n".join(whitespace + matchings);
        footer = '''

%%

int main(int argc, char** argv) {

    yyin = fopen (argv[1] , "r");;
    
    yylex();

    fclose(yyin);
}
'''
        with open("language.lex", "w+") as lexfile:
            lexfile.write(header);
            lexfile.write(flex_patters);
            lexfile.write(footer);



    

if __name__ == "__main__":
    scannerGen = ScannerGenerator()
    scannerGen.generate()     


