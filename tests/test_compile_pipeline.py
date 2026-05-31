import unittest

from semantic_analysis.main import compile as compile_source


def stringify_tac(result):
    return [str(instruction) for instruction in result["tac"]]


class TestCompilePipeline(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def assert_compile_success(self, source, expected_tac):
        result = compile_source(source)

        self.assertTrue(result["success"], msg=f"Compilation failed with errors: {result.get('errors')}")
        self.assertEqual(stringify_tac(result), expected_tac)

    def assert_compile_failure(self, source):
        result = compile_source(source)

        self.assertFalse(result["success"], msg="Compilation unexpectedly succeeded")
        self.assertTrue(result["errors"], msg="Compilation failed without reporting errors")
        return [str(error) for error in result["errors"]]

    def test_factorial_example_generates_expected_tac(self):
        source = """
int factorial(int n) {
    int resultado = 1;
    while (n > 1) {
        resultado = resultado * n;
        n = n - 1;
    }
    return resultado;
}

int main() {
    int num = 5;
    int fact;
    fact = factorial(num);
    return 0;
}
"""

        expected_tac = [
            "factorial:",
            "t1 = 1",
            "resultado = t1",
            "L1:",
            "t2 = n",
            "t3 = 1",
            "t4 = t2 > t3",
            "if t4 == 0 goto L2",
            "t5 = resultado",
            "t6 = n",
            "t7 = t5 * t6",
            "resultado = t7",
            "t8 = n",
            "t9 = 1",
            "t10 = t8 - t9",
            "n = t10",
            "goto L1",
            "L2:",
            "t11 = resultado",
            "return t11",
            "main:",
            "t12 = 5",
            "num = t12",
            "t13 = num",
            "param t13",
            "t14 = call factorial, 1",
            "fact = t14",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_arithmetic_precedence_generates_nested_temporaries(self):
        source = """
int main() {
    int x = 2 + 3 * 4;
    return 0;
}
"""

        expected_tac = [
            "main:",
            "t1 = 2",
            "t2 = 3",
            "t3 = 4",
            "t4 = t2 * t3",
            "t5 = t1 + t4",
            "x = t5",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_function_call_with_two_arguments_generates_params_in_order(self):
        source = """
int sum(int a, int b) {
    return a + b;
}

int main() {
    int result;
    result = sum(2, 3);
    return 0;
}
"""

        expected_tac = [
            "sum:",
            "t1 = a",
            "t2 = b",
            "t3 = t1 + t2",
            "return t3",
            "main:",
            "t4 = 2",
            "param t4",
            "t5 = 3",
            "param t5",
            "t6 = call sum, 2",
            "result = t6",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_if_else_generates_branch_labels_and_jumps(self):
        source = """
int main() {
    int x = 1;
    if (x < 2) {
        x = x + 3;
    } else {
        x = x - 4;
    }
    return 0;
}
"""

        expected_tac = [
            "main:",
            "t1 = 1",
            "x = t1",
            "t2 = x",
            "t3 = 2",
            "t4 = t2 < t3",
            "if t4 == 0 goto L1",
            "t5 = x",
            "t6 = 3",
            "t7 = t5 + t6",
            "x = t7",
            "goto L2",
            "L1:",
            "t8 = x",
            "t9 = 4",
            "t10 = t8 - t9",
            "x = t10",
            "L2:",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_while_loop_generates_back_edge_and_exit_label(self):
        source = """
int main() {
    int x = 3;
    while (x > 0) {
        x = x - 1;
    }
    return 0;
}
"""

        expected_tac = [
            "main:",
            "t1 = 3",
            "x = t1",
            "L1:",
            "t2 = x",
            "t3 = 0",
            "t4 = t2 > t3",
            "if t4 == 0 goto L2",
            "t5 = x",
            "t6 = 1",
            "t7 = t5 - t6",
            "x = t7",
            "goto L1",
            "L2:",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_increment_statement_expands_to_assignment_sequence(self):
        source = """
int main() {
    int x = 0;
    x++;
    return 0;
}
"""

        expected_tac = [
            "main:",
            "t1 = 0",
            "x = t1",
            "t2 = x",
            "t3 = 1",
            "t4 = t2 + t3",
            "x = t4",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_non_main_function_gets_implicit_return_when_missing(self):
        source = """
int noop() {
    int x = 1;
}

int main() {
    return 0;
}
"""

        expected_tac = [
            "noop:",
            "t1 = 1",
            "x = t1",
            "return",
            "main:",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_declaration_without_initializer_emits_no_assignment(self):
        source = """
int main() {
    int x;
    return 0;
}
"""

        expected_tac = [
            "main:",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_function_call_argument_expression_is_evaluated_before_param(self):
        source = """
int twice(int value) {
    return value + value;
}

int main() {
    int x = 4;
    int y;
    y = twice(x + 1);
    return 0;
}
"""

        expected_tac = [
            "twice:",
            "t1 = value",
            "t2 = value",
            "t3 = t1 + t2",
            "return t3",
            "main:",
            "t4 = 4",
            "x = t4",
            "t5 = x",
            "t6 = 1",
            "t7 = t5 + t6",
            "param t7",
            "t8 = call twice, 1",
            "y = t8",
            "return 0",
        ]

        self.assert_compile_success(source, expected_tac)

    def test_lexical_errors_stop_compilation(self):
        source = """
int main() {
    @
    return 0;
}
"""

        errors = self.assert_compile_failure(source)

        self.assertTrue(any("@" in error or "invalid" in error.lower() for error in errors), errors)

    def test_parser_errors_are_returned_without_running_semantic_analysis(self):
        source = """
int main() {
    x = 1;
    return 0;
}
"""

        errors = self.assert_compile_failure(source)

        self.assertIn("Undefined variable 'x' at line 3", errors)

    def test_semantic_errors_are_returned_for_duplicate_functions(self):
        source = """
int foo() {
    return 1;
}

int foo() {
    return 2;
}
"""

        errors = self.assert_compile_failure(source)

        self.assertTrue(any("function 'foo' already declared" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()