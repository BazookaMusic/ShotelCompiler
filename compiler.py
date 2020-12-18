#!/usr/bin/python3
from tokenizer import TokenConverter
from parser import Parser
import sys
import os
import subprocess

if __name__ == "__main__":
    sourceFile = sys.argv[1]

    if not os.path.exists(sourceFile):
        raise FileNotFoundError(sourceFile)
        exit(-1)
    
    tokenizerText = subprocess.check_output(["./scanner", sourceFile])
    utf8lines = map(lambda text: text.decode("utf-8"), tokenizerText.splitlines())

    tokenizer = TokenConverter(utf8lines)
    tokens = tokenizer.tokens

    parser = Parser(tokens)

    program = parser.Program()
    

