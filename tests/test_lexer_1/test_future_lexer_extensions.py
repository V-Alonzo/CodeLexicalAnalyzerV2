import unittest

from Lexer.Lexer import Lexer, TokenClassifier


def tokenize(source: str):
    return Lexer(source).tokenize()


def supports(*token_names: str) -> bool:
    available_token_names = set(TokenClassifier.tokens.values())
    return all(token_name in available_token_names for token_name in token_names)


def assert_token_specs(source: str, expected):
    tokens, _ = tokenize(source)
    actual = [(token.type, token.value) for token in tokens]

    assert len(actual) == len(expected)

    for (actual_type, actual_value), (expected_type, expected_value) in zip(actual, expected):
        assert actual_type == expected_type
        if isinstance(expected_value, tuple):
            if actual_value != expected_value:
                assert actual_value in expected_value
        else:
            assert actual_value == expected_value


class TestFutureLexerExtensions(unittest.TestCase):
    @unittest.skipUnless(supports("AND"), "AND aun no existe en TokenClassifier.tokens")
    def test_and_cases(self):
        cases = [
            ("and-if", "if (a && b) {}", [("IF", "if"), ("LPAREN", "("), ("IDENTIFIER", "a"), ("AND", "&&"), ("IDENTIFIER", "b"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("and-tight", "ready && valid;", [("IDENTIFIER", "ready"), ("AND", "&&"), ("IDENTIFIER", "valid"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("and-while", "while (x > 0 && y > 0) {}", [("WHILE", "while"), ("LPAREN", "("), ("IDENTIFIER", "x"), ("GREATER", ">"), ("NUMBER", 0), ("AND", "&&"), ("IDENTIFIER", "y"), ("GREATER", ">"), ("NUMBER", 0), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("and-chain", "flag = a && b && c;", [("IDENTIFIER", "flag"), ("ASSIGN", "="), ("IDENTIFIER", "a"), ("AND", "&&"), ("IDENTIFIER", "b"), ("AND", "&&"), ("IDENTIFIER", "c"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("and-return", "return a && b;", [("RETURN", "return"), ("IDENTIFIER", "a"), ("AND", "&&"), ("IDENTIFIER", "b"), ("SEMICOLON", ";"), ("EOF", None)]),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                assert_token_specs(source, expected)

    @unittest.skipUnless(supports("OR"), "OR aun no existe en TokenClassifier.tokens")
    def test_or_cases(self):
        cases = [
            ("or-if", "if (a || b) {}", [("IF", "if"), ("LPAREN", "("), ("IDENTIFIER", "a"), ("OR", "||"), ("IDENTIFIER", "b"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("or-tight", "left || right;", [("IDENTIFIER", "left"), ("OR", "||"), ("IDENTIFIER", "right"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("or-while", "while (a || b || c) {}", [("WHILE", "while"), ("LPAREN", "("), ("IDENTIFIER", "a"), ("OR", "||"), ("IDENTIFIER", "b"), ("OR", "||"), ("IDENTIFIER", "c"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("or-nested", "if ((x == y) || done) {}", [("IF", "if"), ("LPAREN", "("), ("LPAREN", "("), ("IDENTIFIER", "x"), ("EQUAL", "=="), ("IDENTIFIER", "y"), ("RPAREN", ")"), ("OR", "||"), ("IDENTIFIER", "done"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("or-return", "return a || b;", [("RETURN", "return"), ("IDENTIFIER", "a"), ("OR", "||"), ("IDENTIFIER", "b"), ("SEMICOLON", ";"), ("EOF", None)]),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                assert_token_specs(source, expected)

    @unittest.skipUnless(supports("NOT"), "NOT aun no existe en TokenClassifier.tokens")
    def test_not_cases(self):
        cases = [
            ("not-if", "if (! flag) {}", [("IF", "if"), ("LPAREN", "("), ("NOT", "!"), ("IDENTIFIER", "flag"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("not-assignment", "result = ! ready;", [("IDENTIFIER", "result"), ("ASSIGN", "="), ("NOT", "!"), ("IDENTIFIER", "ready"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("not-while", "while (! (x < y)) {}", [("WHILE", "while"), ("LPAREN", "("), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "x"), ("LESS", "<"), ("IDENTIFIER", "y"), ("RPAREN", ")"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("not-return", "return ! a;", [("RETURN", "return"), ("NOT", "!"), ("IDENTIFIER", "a"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("double-not", "! ! flag;", [("NOT", "!"), ("NOT", "!"), ("IDENTIFIER", "flag"), ("SEMICOLON", ";"), ("EOF", None)]),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                assert_token_specs(source, expected)

    @unittest.skipUnless(
        supports("AND", "OR", "NOT", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL", "HEX_NUMBER"),
        "Las extensiones logicas, comparativas y hexadecimales aun no existen en TokenClassifier.tokens",
    )
    def test_combined_cases(self):
        cases = [
            ("combined-compare-and", "if (x != y && y <= z) {}", [("IF", "if"), ("LPAREN", "("), ("IDENTIFIER", "x"), ("NOT_EQUAL", "!="), ("IDENTIFIER", "y"), ("AND", "&&"), ("IDENTIFIER", "y"), ("LESS_EQUAL", "<="), ("IDENTIFIER", "z"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("combined-hex-or-not", "if (x >= 0xFF || ! done) {}", [("IF", "if"), ("LPAREN", "("), ("IDENTIFIER", "x"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0xFF", 255)), ("OR", "||"), ("NOT", "!"), ("IDENTIFIER", "done"), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("combined-precedence", "value = ! a || b && c;", [("IDENTIFIER", "value"), ("ASSIGN", "="), ("NOT", "!"), ("IDENTIFIER", "a"), ("OR", "||"), ("IDENTIFIER", "b"), ("AND", "&&"), ("IDENTIFIER", "c"), ("SEMICOLON", ";"), ("EOF", None)]),
            ("combined-loop", "while (left <= right && right != 0x0) {}", [("WHILE", "while"), ("LPAREN", "("), ("IDENTIFIER", "left"), ("LESS_EQUAL", "<="), ("IDENTIFIER", "right"), ("AND", "&&"), ("IDENTIFIER", "right"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0x0", 0)), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("combined-return", "return start >= 0x10 || end <= 0x20 && ! halt;", [("RETURN", "return"), ("IDENTIFIER", "start"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0x10", 16)), ("OR", "||"), ("IDENTIFIER", "end"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0x20", 32)), ("AND", "&&"), ("NOT", "!"), ("IDENTIFIER", "halt"), ("SEMICOLON", ";"), ("EOF", None)]),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                assert_token_specs(source, expected)

    @unittest.skipUnless(
        supports("AND", "OR", "NOT", "NOT_EQUAL", "LESS_EQUAL", "GREATER_EQUAL", "HEX_NUMBER"),
        "Las extensiones completas aun no existen en TokenClassifier.tokens",
    )
    def test_all_new_features_together(self):
        cases = [
            ("all-if", "if (! (a != 0xFF) && b <= 0xA3 || c >= 0x10) {}", [("IF", "if"), ("LPAREN", "("), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "a"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0xFF", 255)), ("RPAREN", ")"), ("AND", "&&"), ("IDENTIFIER", "b"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0xA3", 163)), ("OR", "||"), ("IDENTIFIER", "c"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0x10", 16)), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("all-while", "while (! (left != 0x1) && mid <= 0x2 || right >= 0x3) {}", [("WHILE", "while"), ("LPAREN", "("), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "left"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0x1", 1)), ("RPAREN", ")"), ("AND", "&&"), ("IDENTIFIER", "mid"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0x2", 2)), ("OR", "||"), ("IDENTIFIER", "right"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0x3", 3)), ("RPAREN", ")"), ("LBRACE", "{"), ("RBRACE", "}"), ("EOF", None)]),
            ("all-return", "return ! (a != 0x0) && b <= 0x1 || c >= 0x2;", [("RETURN", "return"), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "a"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0x0", 0)), ("RPAREN", ")"), ("AND", "&&"), ("IDENTIFIER", "b"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0x1", 1)), ("OR", "||"), ("IDENTIFIER", "c"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0x2", 2)), ("SEMICOLON", ";"), ("EOF", None)]),
            ("all-assignment-a", "result = ! (x != 0xAA) && y <= 0xBB || z >= 0xCC;", [("IDENTIFIER", "result"), ("ASSIGN", "="), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "x"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0xAA", 170)), ("RPAREN", ")"), ("AND", "&&"), ("IDENTIFIER", "y"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0xBB", 187)), ("OR", "||"), ("IDENTIFIER", "z"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0xCC", 204)), ("SEMICOLON", ";"), ("EOF", None)]),
            ("all-assignment-b", "flag = ! (p != 0xDE) && q <= 0xAD || r >= 0xBE;", [("IDENTIFIER", "flag"), ("ASSIGN", "="), ("NOT", "!"), ("LPAREN", "("), ("IDENTIFIER", "p"), ("NOT_EQUAL", "!="), ("HEX_NUMBER", ("0xDE", 222)), ("RPAREN", ")"), ("AND", "&&"), ("IDENTIFIER", "q"), ("LESS_EQUAL", "<="), ("HEX_NUMBER", ("0xAD", 173)), ("OR", "||"), ("IDENTIFIER", "r"), ("GREATER_EQUAL", ">="), ("HEX_NUMBER", ("0xBE", 190)), ("SEMICOLON", ";"), ("EOF", None)]),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                assert_token_specs(source, expected)


def start_tests():
    unittest.main()