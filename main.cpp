#include "ast.hpp"
#include "parser.hpp"
#include "tokens.hpp"
#include <iostream>

int main() {
    Parser parser;
    Tokens tokens;

    tokens.emplace(StringValueToken("aaaaa"));
    std::cout << parser.LID(tokens) << std::endl;
}