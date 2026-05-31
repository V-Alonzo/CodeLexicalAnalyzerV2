import unittest

from Lexer.Lexer import Lexer
from abstract_syntax_tree.parser import Parser
from abstract_syntax_tree.semantic_analyzer import SemanticAnalyzer


def analyze_source(source: str):
    tokens, lexer_errors = Lexer(source).tokenize()
    if lexer_errors:
        raise AssertionError(f"Unexpected lexer errors: {lexer_errors}")

    parser = Parser(tokens)
    program = parser.parse_program()
    if parser.errors:
        raise AssertionError(f"Unexpected parser errors: {parser.errors}")

    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


class TestSemanticAnalyzer(unittest.TestCase):
    def test_valid_program_has_no_semantic_errors(self):
        errors = analyze_source(
            """
int id(int value) {
    return value;
}

int main() {
    int x = 1;
    float y = 2.0;
    x = id(x);
    y = x + y;
    while (x < 3) {
        x++;
    }
    return x;
}
"""
        )

        self.assertEqual(errors, [])

    def test_valid_string_program_has_no_semantic_errors(self):
        errors = analyze_source(
            """
string echo(string value) {
    return value;
}

int main() {
    string message = "hola";
    message = echo(message);
    return 0;
}
"""
        )

        self.assertEqual(errors, [])

    def test_assignment_type_mismatch_is_reported(self):
        errors = analyze_source(
            """
int main() {
    int x;
    x = "hola";
    return 0;
}
"""
        )

        self.assertIn("Type mismatch in assignment to 'x': expected int, found string", errors)

    def test_binary_operation_type_mismatch_is_reported(self):
        errors = analyze_source(
            """
int main() {
    int x;
    x = "hola" + 1;
    return 0;
}
"""
        )

        self.assertIn("Incompatible operand types for '+': string and int", errors)

    def test_return_type_mismatch_is_reported(self):
        errors = analyze_source(
            """
int main() {
    return "hola";
}
"""
        )

        self.assertIn("Return type mismatch in function 'main': expected int, found string", errors)


if __name__ == "__main__":
    unittest.main()