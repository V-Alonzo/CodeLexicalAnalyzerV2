import unittest

from Lexer.Lexer import Lexer


def tokenize(source: str):
    return Lexer(source).tokenize()


def token_fields(source: str):
    tokens, _ = tokenize(source)
    return [(token.type, token.value, token.line, token.column) for token in tokens]


def error_fields(source: str):
    _, errors = tokenize(source)
    return [(token.type, token.value, token.line, token.column) for token in errors]


def token_reprs(source: str):
    tokens, _ = tokenize(source)
    return [repr(token) for token in tokens]


def assert_lex_result(testcase, source: str, expected_tokens, expected_errors):
    testcase.assertEqual(token_fields(source), expected_tokens)
    testcase.assertEqual(error_fields(source), expected_errors)


class TestCurrentLexer(unittest.TestCase):
    def test_prompt_example_matches_expected_output(self):
        source = """
    int x = 42;
    float y = 3.14;
    if (x < y) {
        x = x + 1;
    }
    """

        expected = [
            "Token(INT, 'int', line=2, col=5)",
            "Token(IDENTIFIER, 'x', line=2, col=9)",
            "Token(ASSIGN, '=', line=2, col=11)",
            "Token(NUMBER, '42', line=2, col=13)",
            "Token(SEMICOLON, ';', line=2, col=15)",
            "Token(FLOAT, 'float', line=3, col=5)",
            "Token(IDENTIFIER, 'y', line=3, col=11)",
            "Token(ASSIGN, '=', line=3, col=13)",
            "Token(NUMBER, '3.14', line=3, col=15)",
            "Token(SEMICOLON, ';', line=3, col=19)",
            "Token(IF, 'if', line=4, col=5)",
            "Token(LPAREN, '(', line=4, col=8)",
            "Token(IDENTIFIER, 'x', line=4, col=9)",
            "Token(LESS, '<', line=4, col=11)",
            "Token(IDENTIFIER, 'y', line=4, col=13)",
            "Token(RPAREN, ')', line=4, col=14)",
            "Token(LBRACE, '{', line=4, col=16)",
            "Token(IDENTIFIER, 'x', line=5, col=9)",
            "Token(ASSIGN, '=', line=5, col=11)",
            "Token(IDENTIFIER, 'x', line=5, col=13)",
            "Token(PLUS, '+', line=5, col=15)",
            "Token(NUMBER, '1', line=5, col=17)",
            "Token(SEMICOLON, ';', line=5, col=18)",
            "Token(RBRACE, '}', line=6, col=5)",
            "Token(EOF, 'None', line=7, col=5)",
        ]

        self.assertEqual(token_reprs(source), expected)

    def test_current_lexer_happy_paths(self):
        cases = [
            (
                "assignment",
                "int total = 10;",
                [
                    ("INT", "int", 1, 1),
                    ("IDENTIFIER", "total", 1, 5),
                    ("ASSIGN", "=", 1, 11),
                    ("NUMBER", 10, 1, 13),
                    ("SEMICOLON", ";", 1, 15),
                    ("EOF", None, 1, 16),
                ],
            ),
            (
                "string-literal",
                "return \"ok\";",
                [
                    ("RETURN", "return", 1, 1),
                    ("STRING", "ok", 1, 8),
                    ("SEMICOLON", ";", 1, 12),
                    ("EOF", None, 1, 13),
                ],
            ),
            (
                "string-keyword",
                "string message;",
                [
                    ("STRING", "string", 1, 1),
                    ("IDENTIFIER", "message", 1, 8),
                    ("SEMICOLON", ";", 1, 15),
                    ("EOF", None, 1, 16),
                ],
            ),
            (
                "equality-operator",
                "if (a == b) {}",
                [
                    ("IF", "if", 1, 1),
                    ("LPAREN", "(", 1, 4),
                    ("IDENTIFIER", "a", 1, 5),
                    ("EQUAL", "==", 1, 7),
                    ("IDENTIFIER", "b", 1, 10),
                    ("RPAREN", ")", 1, 11),
                    ("LBRACE", "{", 1, 13),
                    ("RBRACE", "}", 1, 14),
                    ("EOF", None, 1, 15),
                ],
            ),
        ]

        for case_name, source, expected in cases:
            with self.subTest(case=case_name):
                self.assertEqual(token_fields(source), expected)

    def test_unterminated_string_returns_error_token(self):
        self.assertEqual(
            token_fields('"unterminated'),
            [
                ("ERROR", "Unterminated string", 1, 1),
                ("EOF", None, 1, 14),
            ],
        )
        self.assertEqual(
            error_fields('"unterminated'),
            [("ERROR", "Unterminated string", 1, 1)],
        )

    def test_unknown_character_returns_error_token(self):
        self.assertEqual(
            token_fields("name @ value"),
            [
                ("IDENTIFIER", "name", 1, 1),
                ("ERROR", "Carácter desconocido: '@'", 1, 6),
                ("IDENTIFIER", "value", 1, 8),
                ("EOF", None, 1, 13),
            ],
        )
        self.assertEqual(
            error_fields("name @ value"),
            [("ERROR", "Carácter desconocido: '@'", 1, 6)],
        )

    def test_invalid_hex_with_non_hex_digit_returns_error_token(self):
        assert_lex_result(
            self,
            "x = 0xG1;",
            [
                ("IDENTIFIER", "x", 1, 1),
                ("ASSIGN", "=", 1, 3),
                ("ERROR", "Invalid hexadecimal number: 0xG1", 1, 5),
                ("SEMICOLON", ";", 1, 9),
                ("EOF", None, 1, 10),
            ],
            [("ERROR", "Invalid hexadecimal number: 0xG1", 1, 5)],
        )

    def test_invalid_hex_with_invalid_suffix_returns_error_token(self):
        assert_lex_result(
            self,
            "x = 0x1G;",
            [
                ("IDENTIFIER", "x", 1, 1),
                ("ASSIGN", "=", 1, 3),
                ("ERROR", "Invalid hexadecimal number: 0x1G", 1, 5),
                ("SEMICOLON", ";", 1, 9),
                ("EOF", None, 1, 10),
            ],
            [("ERROR", "Invalid hexadecimal number: 0x1G", 1, 5)],
        )

    def test_invalid_hex_without_digits_returns_error_token(self):
        assert_lex_result(
            self,
            "x = 0x;",
            [
                ("IDENTIFIER", "x", 1, 1),
                ("ASSIGN", "=", 1, 3),
                ("ERROR", "Invalid hexadecimal number: 0x", 1, 5),
                ("SEMICOLON", ";", 1, 7),
                ("EOF", None, 1, 8),
            ],
            [("ERROR", "Invalid hexadecimal number: 0x", 1, 5)],
        )

    def test_unterminated_string_after_keyword_returns_error_token(self):
        assert_lex_result(
            self,
            'return "oops',
            [
                ("RETURN", "return", 1, 1),
                ("ERROR", "Unterminated string", 1, 8),
                ("EOF", None, 1, 13),
            ],
            [("ERROR", "Unterminated string", 1, 8)],
        )

    def test_unknown_dollar_character_returns_error_token(self):
        assert_lex_result(
            self,
            "name $ value",
            [
                ("IDENTIFIER", "name", 1, 1),
                ("ERROR", "Carácter desconocido: '$'", 1, 6),
                ("IDENTIFIER", "value", 1, 8),
                ("EOF", None, 1, 13),
            ],
            [("ERROR", "Carácter desconocido: '$'", 1, 6)],
        )

    def test_single_ampersand_returns_error_token(self):
        assert_lex_result(
            self,
            "if (a & b) {}",
            [
                ("IF", "if", 1, 1),
                ("LPAREN", "(", 1, 4),
                ("IDENTIFIER", "a", 1, 5),
                ("ERROR", "Carácter desconocido: '&'", 1, 7),
                ("IDENTIFIER", "b", 1, 9),
                ("RPAREN", ")", 1, 10),
                ("LBRACE", "{", 1, 12),
                ("RBRACE", "}", 1, 13),
                ("EOF", None, 1, 14),
            ],
            [("ERROR", "Carácter desconocido: '&'", 1, 7)],
        )

    def test_single_pipe_returns_error_token(self):
        assert_lex_result(
            self,
            "if (a | b) {}",
            [
                ("IF", "if", 1, 1),
                ("LPAREN", "(", 1, 4),
                ("IDENTIFIER", "a", 1, 5),
                ("ERROR", "Carácter desconocido: '|'", 1, 7),
                ("IDENTIFIER", "b", 1, 9),
                ("RPAREN", ")", 1, 10),
                ("LBRACE", "{", 1, 12),
                ("RBRACE", "}", 1, 13),
                ("EOF", None, 1, 14),
            ],
            [("ERROR", "Carácter desconocido: '|'", 1, 7)],
        )

    def test_trailing_decimal_point_returns_error_token(self):
        assert_lex_result(
            self,
            "value = 3.;",
            [
                ("IDENTIFIER", "value", 1, 1),
                ("ASSIGN", "=", 1, 7),
                ("NUMBER", 3, 1, 9),
                ("ERROR", "Carácter desconocido: '.'", 1, 10),
                ("SEMICOLON", ";", 1, 11),
                ("EOF", None, 1, 12),
            ],
            [("ERROR", "Carácter desconocido: '.'", 1, 10)],
        )

    def test_multiple_unknown_characters_are_reported(self):
        assert_lex_result(
            self,
            "name @ $ value",
            [
                ("IDENTIFIER", "name", 1, 1),
                ("ERROR", "Carácter desconocido: '@'", 1, 6),
                ("ERROR", "Carácter desconocido: '$'", 1, 8),
                ("IDENTIFIER", "value", 1, 10),
                ("EOF", None, 1, 15),
            ],
            [
                ("ERROR", "Carácter desconocido: '@'", 1, 6),
                ("ERROR", "Carácter desconocido: '$'", 1, 8),
            ],
        )

    def test_extra_ampersand_after_and_operator_returns_error_token(self):
        assert_lex_result(
            self,
            "if (a &&& b) {}",
            [
                ("IF", "if", 1, 1),
                ("LPAREN", "(", 1, 4),
                ("IDENTIFIER", "a", 1, 5),
                ("AND", "&&", 1, 7),
                ("ERROR", "Carácter desconocido: '&'", 1, 9),
                ("IDENTIFIER", "b", 1, 11),
                ("RPAREN", ")", 1, 12),
                ("LBRACE", "{", 1, 14),
                ("RBRACE", "}", 1, 15),
                ("EOF", None, 1, 16),
            ],
            [("ERROR", "Carácter desconocido: '&'", 1, 9)],
        )


def start_tests():
    unittest.main()