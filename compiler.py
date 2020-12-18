#!/usr/bin/python3
from tokenizer import TokenConverter
import sys
import os
import subprocess

if __name__ == "__main__":
    sourceFile = sys.argv[1]

    if not os.path.exists(sourceFile):
        raise FileNotFoundError(sourceFile)
        exit(-1)

    sourceFile = '/mnt/c/Users/sodragon/Documents/compiler/sources/source.sd'
    
    tokenizerText = subprocess.check_output(["./scanner", sourceFile])
    utf8lines = map(lambda text: text.decode("utf-8"), tokenizerText.splitlines())

    tokenizer = TokenConverter(utf8lines)
    tokens = tokenizer.tokens
    
    print(tokenizer.tokens)


    b'TYPE\nUID(Cheese)\nASSIGN\nUID(FETA)\nLID(int)\nLID(int)\nLID(int)\nCOMMA\nUID(EDAM)\nLID(int)\nLID(int)\nLID(int)\nCOMMA\nUID(Gouda)\nLID(int)\nLID(bool)\nFN\nUID(A)\nLID(a)\nLID(b)\nLID(c)\nOCURLY\nCASE\nINT(15)\nPLUS\nINT(3)\n|INT(11)\n|INT(12)\n|INT(14)\nCCURLY\n'
