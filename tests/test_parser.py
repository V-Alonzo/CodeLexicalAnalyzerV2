import unittest

from Lexer.Lexer import Lexer
from abstract_syntax_tree.ast_nodes import AssignmentNode, FunctionCallNode
from abstract_syntax_tree.parser import Parser


def parse_source(source: str):
    tokens, errors = Lexer(source).tokenize()
    if errors:
        raise AssertionError(f"Unexpected lexer errors: {errors}")

    parser = Parser(tokens)
    program = parser.parse_program()
    return program, parser.errors


class TestParser(unittest.TestCase):
    def test_function_call_assignment_parses_without_errors(self):
        source = """
int factorial(int n) {
    return n;
}

int main() {
    int num = 5;
    int fact;
    fact = factorial(num);
    return 0;
}
"""

        program, errors = parse_source(source)

        self.assertEqual(errors, [])
        self.assertEqual(len(program.functions), 2)

        main_function = program.functions[1]
        assignment = next(
            statement for statement in main_function.body if isinstance(statement, AssignmentNode)
        )

        self.assertIsInstance(assignment.expression, FunctionCallNode)
        self.assertEqual(assignment.expression.name, "factorial")
        self.assertEqual(len(assignment.expression.arguments), 1)

    def test_assignment_requires_prior_declaration(self):
        _, errors = parse_source(
            """
int main() {
    x = 1;
    return 0;
}
"""
        )

        self.assertIn("Undefined variable 'x' at line 3", errors)

    def test_redeclaration_in_same_scope_reports_error(self):
        _, errors = parse_source(
            """
int main() {
    int x;
    int x;
    return 0;
}
"""
        )

        self.assertIn("Variable 'x' already declared in this scope at line 4", errors)

    def test_nested_block_scope_drops_inner_variables(self):
        _, errors = parse_source(
            """
int main() {
    int x;
    {
        int y;
        y = x;
    }
    y = 1;
    return 0;
}
"""
        )

        self.assertIn("Undefined variable 'y' at line 8", errors)

    def test_nested_block_scope_redeclaration_reports_error(self):
        _, errors = parse_source(
            """
int main() {
    int x;
    {
        int x;
        x = 1;
    }
    x = 2;
    return 0;
}
"""
        )

        self.assertIn("Variable 'x' already declared in this scope at line 5", errors)


if __name__ == "__main__":
    unittest.main()