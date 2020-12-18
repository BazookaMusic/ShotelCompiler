import unittest
from tokenizer import Token
from parser import Parser

class ParserTest(unittest.TestCase):
    def test_type_simple(self):
        parser = Parser([
        Token("TYPE"), Token('UID(Hello)'), Token("ASSIGN"), 
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)"),
        Token("COMMA"),
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)"),
        Token("COMMA"),
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)"),

        Token("TYPE"), Token('UID(Hello)'), Token("ASSIGN"), 
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)"),
        Token("COMMA"),
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)"),
        Token("COMMA"),
            Token("UID(FETA)"), Token("UID(INT)"), Token("UID(INT)")])
        
        expectedOutput = "[DefinitionType(Hello)[Constructor(FETA)['INT', 'INT'], Constructor(FETA)['INT', 'INT'], Constructor(FETA)['INT', 'INT']], DefinitionType(Hello)[Constructor(FETA)['INT', 'INT'], Constructor(FETA)['INT', 'INT'], Constructor(FETA)['INT', 'INT']]]"

        self.assertEqual(expectedOutput, str(parser.Program()))
    
    def test_type_constructor(self):
        source = [
            "TYPE", "UID(AFunc)", "ASSIGN", 
                "UID(COMPOSITE)", "UID(Int)", "UID(Int)", 
                "COMMA", 
                "UID(COMPOSITE2)", "UID(Double)", "UID(Double)"
        ]

        tokens = ParserTest.to_tokens(source)
        parser = Parser(tokens)
        
        expectedTree = "[DefinitionType(AFunc)[Constructor(COMPOSITE)['Int', 'Int'], Constructor(COMPOSITE2)['Double', 'Double']]]"
        self.assertEqual(expectedTree, str(parser.Program()))
    
    def test_type_mixed(self):
        source = [
            "TYPE", "UID(AFunc)", "ASSIGN", 
                "UID(COMPOSITE)", "UID(Int)", "UID(Int)", 
                "COMMA", 
                "UID(COMPOSITE2)", "UID(Double)", "UID(Double)",
                "COMMA",
                "UID(Another)",
                "UID(Int)",
                "UID(Int)",
                "COMMA",
                "UID(EMPTY)"
        ]

        tokens = ParserTest.to_tokens(source)
        parser = Parser(tokens)
        expectedTree = "[DefinitionType(AFunc)[Constructor(COMPOSITE)['Int', 'Int'], Constructor(COMPOSITE2)['Double', 'Double'], Constructor(Another)['Int', 'Int'], Constructor(EMPTY)[]]]"
        self.assertEqual(expectedTree, str(parser.Program()))
        
    
    def test_fn_simple(self):
        parser = Parser([
        Token("FN"), Token('UID(Hello)'), Token("LID(a)"), Token("LID(b)"), 
            Token("OCURLY"), Token("INT(5)"), Token("PLUS"), Token("INT(4)"), Token("PLUS"), Token("INT(5)"), Token("CCURLY")])

        expectedBody = 'BinaryOp(OperationKind.PLUS) INT(5) BinaryOp(OperationKind.PLUS) INT(4) INT(5)'

        self.assertEqual(expectedBody, str(Parser.TreeToString(parser.Program()[0].body)))
    
    def test_fn_comparison(self):
        source = [
            "FN", "UID(TEST)", "LID(a)", "LID(b)", 
            "OCURLY",
                "LID(a)", "EQUAL", "INT(13)",
            "CCURLY"
        ]

        tokens = ParserTest.to_tokens(source)

        parser = Parser(tokens)
        program = parser.Program()
        
        definition = "[DefinitionFn(TokenType.UID(TEST))['a', 'b']]"
        self.assertEqual(definition, str(program))

        expected = "BinaryOp(OperationKind.EQUALS) String(a) INT(13)"
        self.assertEqual(expected, Parser.TreeToString(program[0].body))
    
    def test_fn_add_before_comparison(self):
        source =  [
            "FN", "UID(TEST)", "LID(a)", "LID(b)", 
            "OCURLY",

                "LID(a)", "EQUAL", "INT(13)", "PLUS", "INT(14)", "PLUS", "INT(15)", "EQUAL", "INT(15)",

            "CCURLY"
        ]

        program = ParserTest.get_program(source)

        expected = "BinaryOp(OperationKind.EQUALS) String(a) BinaryOp(OperationKind.EQUALS) BinaryOp(OperationKind.PLUS) INT(13) BinaryOp(OperationKind.PLUS) INT(14) INT(15) INT(15)"
        self.assertEqual(expected, Parser.TreeToString(program[0].body))
    
    def test_fn_mul_before_add(self):
        source =  [
            "FN", "UID(TEST)", "LID(a)", "LID(b)", 
            "OCURLY",

                "LID(a)", "PLUS", "INT(13)", "TIMES", "INT(14)", "PLUS", "INT(15)", "TIMES", "INT(15)",

            "CCURLY"
        ]

        program = ParserTest.get_program(source)

        expected = "BinaryOp(OperationKind.PLUS) String(a) BinaryOp(OperationKind.PLUS) BinaryOp(OperationKind.TIMES) INT(13) INT(14) BinaryOp(OperationKind.TIMES) INT(15) INT(15)"
        self.assertEqual(expected, Parser.TreeToString(program[0].body))
    
    def test_fn_or_before_mul(self):
        source =  [
            "FN", "UID(TEST)", "LID(a)", "LID(b)", 
            "OCURLY",

                "LID(a)", "TIMES", "INT(13)", "OR", "INT(14)", "TIMES", "INT(15)", "OR", "INT(15)",

            "CCURLY"
        ]

        program = ParserTest.get_program(source)

        expected = "BinaryOp(OperationKind.TIMES) String(a) BinaryOp(OperationKind.TIMES) BinaryOp(OperationKind.OR) INT(13) INT(14) BinaryOp(OperationKind.OR) INT(15) INT(15)"
        self.assertEqual(expected, Parser.TreeToString(program[0].body))
    
    def test_complex_1(self):
        source = [
            "FN", "UID(TEST)", "LID(a)", "LID(b)",
            "OCURLY",
                "INT(15)", "PLUS", "INT(16)", "TIMES", "INT(23)" , "OR", "INT(17)", "AND", "INT(25)" , "XOR", "INT(35)", "EQUAL", "INT(17)", "NEQUAL", "INT(21)", 
                "PLUS", 
                "CASE", "OPAR", "INT(15)", "PLUS", "INT(32)", "CPAR",
                "PATTERN", "LID(a)", "ARROW", "OCURLY", "INT(3)", "PLUS", "INT(4)", "CCURLY",
                "PATTERN", "UID(TEST)", "LID(a)", "LID(b)", "ARROW", "OCURLY", "INT(3)", "PLUS", "INT(4)", "CCURLY",
                "PATTERN", "LID(b)", "ARROW", "OCURLY", "INT(4)", "MODULO", "INT(5)", "CCURLY",
                "PATTERN", "LID(c)", "ARROW", "OCURLY", "INT(4)", "RSHIFT", "INT(5)", "CCURLY",
                "PATTERN", "LID(c)", "ARROW", "OCURLY", "OPAR","INT(4)", "RSHIFT", "INT(5)","CPAR", "PLUS", "INT(5)", "CCURLY",
            "CCURLY"
        ]

        program = ParserTest.get_program(source)

    
    def to_tokens(tokens):
        return [Token(token) for token in tokens]
    
    def get_program(source):
        parser = Parser(ParserTest.to_tokens(source))
        return parser.Program()

    

if __name__ == "__main__":
    unittest.main()