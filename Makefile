scanner.cpp: language.lex
	flex -o $@ $<

language.lex: scannerGenerator.py
	python3 $<

scanner: scanner.cpp
	clang++ -o $@ $<

main: scanner.o parser.o
	clang++ -o scomp main.cpp

clean:
	rm *.o