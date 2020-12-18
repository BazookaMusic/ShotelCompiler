
%option noyywrap
%{
#include <iostream>
#include <stdio.h>

%}

%%
[ \n]+ {}
\+  { std::cout << "PLUS" << std::endl; }
- { std::cout << "MINUS" << std::endl; }
\/ { std::cout << "DIVIDE" << std::endl; }
\*  { std::cout << "TIMES" << std::endl; }
\%  { std::cout << "MODULO" << std::endl; }
\<\<  { std::cout << "LSHIFT" << std::endl; }
\>\>  { std::cout << "RSHIFT" << std::endl; }
and  { std::cout << "AND" << std::endl; }
or  { std::cout << "OR" << std::endl; }
xor  { std::cout << "XOR" << std::endl; }
\!  { std::cout << "NOT" << std::endl; }
[0-9]+  { std::cout << "INT" << "(" << yytext << ")" << std::endl; }
fn  { std::cout << "FN" << std::endl; }
type  { std::cout << "TYPE" << std::endl; }
case  { std::cout << "CASE" << std::endl; }
\| { std::cout << "PATTERN" << std::endl; }
\{ { std::cout << "OCURLY" << std::endl; }
\}  { std::cout << "CCURLY" << std::endl; }
\(  { std::cout << "OPAR" << std::endl; }
\)  { std::cout << "CPAR" << std::endl; }
,   { std::cout << "COMMA" << std::endl; }
=> { std::cout << "ARROW" << std::endl; }
= { std::cout << "ASSIGN" << std::endl; }
== { std::cout << "EQUAL" << std::endl; }
!= { std::cout << "NEQUAL" << std::endl; }
[a-z][a-zA-Z]* { std::cout << "LID" << "(" << yytext << ")" << std::endl; }
[A-Z][a-zA-Z]*  { std::cout << "UID" << "(" << yytext << ")" << std::endl; }
\"(([^\"]|\\\")*[^\\])?\"  { std::cout << "LITERAL" << "(" << yytext << ")" << std::endl; }

%%

int main(int argc, char** argv) {

    yyin = fopen (argv[1] , "r");;
    
    yylex();

    fclose(yyin);
}
