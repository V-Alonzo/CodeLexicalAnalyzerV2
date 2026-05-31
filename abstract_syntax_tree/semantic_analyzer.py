from abstract_syntax_tree.ast_nodes import (
    AssignmentNode,
    BinaryOpNode,
    DeclarationNode,
    FunctionCallNode,
    FunctionNode,
    IdentifierNode,
    IfNode,
    NumberNode,
    Program,
    ReturnNode,
    StringNode,
    UnaryOpNode,
    WhileNode,
)
from abstract_syntax_tree.symbol_table import SymbolTable


class SemanticAnalyzer:
    def __init__(self):
        self.errors = []
        self.function_signatures = {}
        self.symbol_table = SymbolTable()
        self.current_function = None

    def analyze(self, program):
        self.errors = []
        self.function_signatures = {}
        self.symbol_table = SymbolTable()
        self.current_function = None

        if not isinstance(program, Program):
            return self.errors

        for function in program.functions:
            self.function_signatures[function.name] = {
                "return_type": function.return_type,
                "parameters": function.parameters,
            }

        for function in program.functions:
            self._analyze_function(function)

        return self.errors

    def _enter_scope(self):
        self.symbol_table.enter_scope()

    def _exit_scope(self):
        self.symbol_table.exit_scope()

    def _declare(self, name, var_type):
        try:
            self.symbol_table.declare(name, var_type)
        except Exception as exc:
            self.errors.append(str(exc))

    def _lookup(self, name):
        return self.symbol_table.lookup(name)

    def _is_numeric(self, value_type):
        return value_type in {"int", "float"}

    def _is_assignable(self, expected_type, actual_type):
        if expected_type is None or actual_type is None:
            return False
        if expected_type == actual_type:
            return True
        return expected_type == "float" and actual_type == "int"

    def _common_numeric_type(self, left_type, right_type):
        if not self._is_numeric(left_type) or not self._is_numeric(right_type):
            return None
        if "float" in {left_type, right_type}:
            return "float"
        return "int"

    def _analyze_function(self, function):
        self.current_function = function
        self._enter_scope()
        try:
            for param_type, param_name in function.parameters:
                self._declare(param_name, param_type)
            self._analyze_statements(function.body)
        finally:
            self._exit_scope()
            self.current_function = None

    def _analyze_statements(self, statements, create_scope=False):
        if create_scope:
            self._enter_scope()
        try:
            for statement in statements:
                self._analyze_statement(statement)
        finally:
            if create_scope:
                self._exit_scope()

    def _analyze_statement(self, statement):
        if isinstance(statement, list):
            self._analyze_statements(statement, create_scope=True)
            return

        if isinstance(statement, DeclarationNode):
            self._declare(statement.name, statement.var_type)
            if statement.initializer is not None:
                initializer_type = self._infer_expression_type(statement.initializer)
                if initializer_type and not self._is_assignable(statement.var_type, initializer_type):
                    self.errors.append(
                        f"Type mismatch in declaration of '{statement.name}': "
                        f"expected {statement.var_type}, found {initializer_type}"
                    )
            return

        if isinstance(statement, AssignmentNode):
            variable_type = self._lookup(statement.name)
            expression_type = self._infer_expression_type(statement.expression)
            if variable_type and expression_type and not self._is_assignable(variable_type, expression_type):
                self.errors.append(
                    f"Type mismatch in assignment to '{statement.name}': "
                    f"expected {variable_type}, found {expression_type}"
                )
            return

        if isinstance(statement, IfNode):
            self._infer_expression_type(statement.condition)
            self._analyze_statements(statement.if_body, create_scope=True)
            if statement.else_body is not None:
                self._analyze_statements(statement.else_body, create_scope=True)
            return

        if isinstance(statement, WhileNode):
            self._infer_expression_type(statement.condition)
            self._analyze_statements(statement.body, create_scope=True)
            return

        if isinstance(statement, ReturnNode):
            expression_type = self._infer_expression_type(statement.expression)
            expected_type = self.current_function.return_type if self.current_function else None
            if expected_type and not self._is_assignable(expected_type, expression_type):
                self.errors.append(
                    f"Return type mismatch in function '{self.current_function.name}': "
                    f"expected {expected_type}, found {expression_type}"
                )

    def _infer_expression_type(self, expression):
        if expression is None:
            return None

        if isinstance(expression, NumberNode):
            return "float" if isinstance(expression.value, float) else "int"

        if isinstance(expression, StringNode):
            return "string"

        if isinstance(expression, IdentifierNode):
            return self._lookup(expression.name)

        if isinstance(expression, FunctionCallNode):
            signature = self.function_signatures.get(expression.name)
            if signature is None:
                self.errors.append(f"Call to undefined function '{expression.name}'")
                return None

            expected_params = signature["parameters"]
            if len(expression.arguments) != len(expected_params):
                self.errors.append(
                    f"Argument count mismatch in call to '{expression.name}': "
                    f"expected {len(expected_params)}, found {len(expression.arguments)}"
                )
            else:
                for argument, (param_type, _) in zip(expression.arguments, expected_params):
                    argument_type = self._infer_expression_type(argument)
                    if argument_type and not self._is_assignable(param_type, argument_type):
                        self.errors.append(
                            f"Argument type mismatch in call to '{expression.name}': "
                            f"expected {param_type}, found {argument_type}"
                        )

            return signature["return_type"]

        if isinstance(expression, UnaryOpNode):
            operand_type = self._infer_expression_type(expression.operand)
            if expression.operator == "-":
                if not self._is_numeric(operand_type):
                    self.errors.append(
                        f"Invalid unary operation '{expression.operator}' for type {operand_type}"
                    )
                    return None
                return operand_type

            if expression.operator == "!":
                if not self._is_numeric(operand_type):
                    self.errors.append(
                        f"Invalid unary operation '{expression.operator}' for type {operand_type}"
                    )
                    return None
                return "int"

            return None

        if isinstance(expression, BinaryOpNode):
            left_type = self._infer_expression_type(expression.left)
            right_type = self._infer_expression_type(expression.right)
            operator = expression.operator

            if operator in {"+", "-", "*", "/", "%"}:
                result_type = self._common_numeric_type(left_type, right_type)
                if result_type is None:
                    self.errors.append(
                        f"Incompatible operand types for '{operator}': {left_type} and {right_type}"
                    )
                    return None
                return result_type

            if operator in {"<", ">", "<=", ">="}:
                if self._common_numeric_type(left_type, right_type) is None:
                    self.errors.append(
                        f"Incompatible operand types for '{operator}': {left_type} and {right_type}"
                    )
                    return None
                return "int"

            if operator in {"==", "!="}:
                if left_type == right_type:
                    return "int"
                if self._common_numeric_type(left_type, right_type) is not None:
                    return "int"
                self.errors.append(
                    f"Incompatible operand types for '{operator}': {left_type} and {right_type}"
                )
                return None

            if operator in {"&&", "||"}:
                if self._common_numeric_type(left_type, right_type) is None:
                    self.errors.append(
                        f"Incompatible operand types for '{operator}': {left_type} and {right_type}"
                    )
                    return None
                return "int"

        return None