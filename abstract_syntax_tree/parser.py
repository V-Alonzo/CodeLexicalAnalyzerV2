# parser.py
from Lexer.Lexer import TokenClassifier
from abstract_syntax_tree.ast_nodes import *
from abstract_syntax_tree.symbol_table import SymbolTable

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []
        self.symbol_table = SymbolTable()
    
    def current_token(self):
        """Retorna el token actual"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def peek(self):
        """Observa el siguiente token sin consumirlo"""
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None
    
    def consume(self, expected_type):
        """Consume el token actual si es del tipo esperado"""
        token = self.current_token()
        if token and token.type == expected_type:
            self.position += 1
            return token
        else:
            expected = expected_type
            found = token.type if token else "EOF"
            self.errors.append(
                f"Syntax error at line {token.line if token else '?'}, "
                f"column {token.column if token else '?'}: "
                f"expected {expected}, found {found}"
            )
            return None
    
    def match(self, expected_type):
        """Verifica si el token actual es del tipo esperado sin consumirlo"""
        token = self.current_token()
        return token and token.type == expected_type
    
    def synchronize(self, sync_tokens):
        """Recuperación de errores: salta tokens hasta encontrar uno en sync_tokens"""
        while self.current_token():
            if self.current_token().type in sync_tokens:
                break
            self.position += 1

    def _is_type_token(self, token=None):
        token = token or self.current_token()
        return token and token.type in [
            TokenClassifier.tokens["int"],
            TokenClassifier.tokens["float"],
            TokenClassifier.tokens["STRING"],
        ]

    def _declare_variable(self, name_token, var_type):
        if self.symbol_table.lookup(name_token.value) is not None:
            self.errors.append(
                f"Variable '{name_token.value}' already declared in this scope at line {name_token.line}"
            )
            return False
        self.symbol_table.declare(name_token.value, var_type)
        return True

    def _require_declared_variable(self, name_token):
        if self.symbol_table.lookup(name_token.value) is None:
            self.errors.append(f"Undefined variable '{name_token.value}' at line {name_token.line}")
            return False
        return True

    def _parse_body_until(self, stop_tokens):
        """Parsea declaraciones y sentencias asegurando avance incluso ante errores."""
        items = []
        while self.current_token() and self.current_token().type not in stop_tokens:
            start_position = self.position
            if self._is_type_token():
                item = self.parse_declaration()
            else:
                item = self.parse_statement()
            if item:
                if isinstance(item, list):
                    items.extend(item)
                else:
                    items.append(item)
            elif self.position == start_position:
                self.position += 1
        return items
    
    # ============ Funciones de parseo por no terminal ============
    
    def parse_program(self):
        """programa → funcion*"""
        functions = []
        while self._is_type_token():
            start_position = self.position
            func = self.parse_function()
            if func:
                functions.append(func)
            elif self.position == start_position:
                self.position += 1
        return Program(functions)
    
    def parse_function(self):
        """funcion → tipo IDENTIFIER LPAREN parametros RPAREN LBRACE declaraciones* sentencias* RBRACE"""
        # Tipo de retorno
        return_type_token = self.current_token()
        if not return_type_token:
            return None
        
        return_type = None
        if return_type_token.type == TokenClassifier.tokens["int"]:
            return_type = "int"
            self.consume(TokenClassifier.tokens["int"])
        elif return_type_token.type == TokenClassifier.tokens["float"]:
            return_type = "float"
            self.consume(TokenClassifier.tokens["float"])
        elif return_type_token.type == TokenClassifier.tokens["STRING"]:
            return_type = "string"
            self.consume(TokenClassifier.tokens["STRING"])
        else:
            self.errors.append(f"Expected type at line {return_type_token.line}")
            return None
        
        # Nombre de la función
        name_token = self.consume(TokenClassifier.tokens["IDENTIFIER"])
        if not name_token:
            return None
        func_name = name_token.value

        self.symbol_table.enter_scope()
        scope_entered = True
        
        try:
            # Parámetros
            if not self.consume(TokenClassifier.tokens["("]):
                return None
            
            parameters = self.parse_parameters()
            
            if not self.consume(TokenClassifier.tokens[")"]):
                return None
            
            if not self.consume(TokenClassifier.tokens["{"]):
                return None
            
            body = self._parse_body_until([TokenClassifier.tokens["}"], TokenClassifier.tokens["EOF"]])
            
            if not self.consume(TokenClassifier.tokens["}"]):
                return None

            return FunctionNode(return_type, func_name, parameters, body)
        finally:
            if scope_entered:
                self.symbol_table.exit_scope()
    
    def parse_parameters(self):
        """parametros → (tipo IDENTIFIER (COMMA tipo IDENTIFIER)*)? """
        parameters = []
        
        if self.match(TokenClassifier.tokens[")"]):
            return parameters
        
        # Primer parámetro
        param_type = self.parse_type()
        if not param_type:
            return parameters
        
        name_token = self.consume(TokenClassifier.tokens["IDENTIFIER"])
        if name_token:
            self._declare_variable(name_token, param_type)
            parameters.append((param_type, name_token.value))
        
        # Parámetros adicionales
        while self.match(TokenClassifier.tokens[","]):
            self.consume(TokenClassifier.tokens[","])
            param_type = self.parse_type()
            if not param_type:
                break
            name_token = self.consume(TokenClassifier.tokens["IDENTIFIER"])
            if name_token:
                self._declare_variable(name_token, param_type)
                parameters.append((param_type, name_token.value))
        
        return parameters
    
    def parse_type(self):
        """tipo → INT | FLOAT"""
        if self.match(TokenClassifier.tokens["int"]):
            self.consume(TokenClassifier.tokens["int"])
            return "int"
        elif self.match(TokenClassifier.tokens["float"]):
            self.consume(TokenClassifier.tokens["float"])
            return "float"
        elif self.match(TokenClassifier.tokens["STRING"]):
            self.consume(TokenClassifier.tokens["STRING"])
            return "string"
        return None
    
    def parse_declaration(self):
        """declaracion → tipo IDENTIFIER (ASSIGN expresion)? SEMICOLON"""
        var_type = self.parse_type()
        if not var_type:
            return None
        
        name_token = self.consume(TokenClassifier.tokens["IDENTIFIER"])
        if not name_token:
            return None

        is_valid_declaration = self._declare_variable(name_token, var_type)
        
        initializer = None
        if self.match(TokenClassifier.tokens["="]):
            self.consume(TokenClassifier.tokens["="])
            initializer = self.parse_expression()
        
        if not self.consume(TokenClassifier.tokens[";"]):
            return None

        if not is_valid_declaration:
            return None
        
        return DeclarationNode(var_type, name_token.value, initializer)
    
    def parse_statement(self):
        """sentencia → asignacion | if | while | return | print | bloque"""
        token = self.current_token()
        if not token:
            return None
        
        if token.type == TokenClassifier.tokens["IDENTIFIER"]:
            # Podría ser asignación o llamada a print (pero print es reservada)
            return self.parse_assignment()
        elif token.type == TokenClassifier.tokens["if"]:
            return self.parse_if()
        elif token.type == TokenClassifier.tokens["while"]:
            return self.parse_while()
        elif token.type == TokenClassifier.tokens["for"]:
            return self.parse_for()
        elif token.type == TokenClassifier.tokens["print"]:
            return self.parse_print()
        elif token.type == TokenClassifier.tokens["do"]:
            return self.parse_do_while()
        elif token.type == TokenClassifier.tokens["return"]:
            return self.parse_return()
        elif token.type == TokenClassifier.tokens["{"]:
            return self.parse_block()
        else:
            self.errors.append(f"Unexpected token {token.type} at line {token.line}")
            self.synchronize([TokenClassifier.tokens[";"], TokenClassifier.tokens["}"]])
            if self.match(TokenClassifier.tokens[";"]):
                self.consume(TokenClassifier.tokens[";"])
            return None
    
    def parse_assignment(self, required_semicolon=True):
        """asignacion → IDENTIFIER ASSIGN expresion SEMICOLON"""
        name_token = self.consume(TokenClassifier.tokens["IDENTIFIER"])
        if not name_token:
            return None

        target_declared = self._require_declared_variable(name_token)
        
        # Podría ser incremento/decremento (e.g., x++ o x--) o asignación normal
        binaryOpNode = None
        if self.match(TokenClassifier.tokens["++"]):
            self.consume(TokenClassifier.tokens["++"])
            binaryOpNode = BinaryOpNode('+', IdentifierNode(name_token.value), NumberNode(1))
        elif self.match(TokenClassifier.tokens["--"]):
            self.consume(TokenClassifier.tokens["--"])
            binaryOpNode = BinaryOpNode('-', IdentifierNode(name_token.value), NumberNode(1))

        if binaryOpNode:
            if required_semicolon and not self.consume(TokenClassifier.tokens[";"]):
                return None
            if not target_declared:
                return None
            return AssignmentNode(name_token.value, binaryOpNode)
        
        if not self.consume(TokenClassifier.tokens["="]):
            return None
        
        expr = self.parse_expression()
        if not expr:
            return None
        
        if not self.consume(TokenClassifier.tokens[";"]) and required_semicolon:
            return None

        if not target_declared:
            return None
        
        return AssignmentNode(name_token.value, expr)
    
    def parse_if(self):
        """if → IF LPAREN expresion RPAREN sentencia (ELSE sentencia)?"""
        self.consume(TokenClassifier.tokens["if"])
        
        if not self.consume(TokenClassifier.tokens["("]):
            return None
        
        condition = self.parse_expression()
        if not condition:
            return None
        
        if not self.consume(TokenClassifier.tokens[")"]):
            return None
        
        # Cuerpo del if
        if_body = []
        if self.match(TokenClassifier.tokens["{"]):
            if_body = self.parse_block()
        else:
            stmt = self.parse_statement()
            if stmt:
                if_body = [stmt]
        
        # Cuerpo del else (opcional)
        else_body = None
        if self.match(TokenClassifier.tokens["else"]):
            self.consume(TokenClassifier.tokens["else"])
            if self.match(TokenClassifier.tokens["{"]):
                else_body = self.parse_block()
            else:
                stmt = self.parse_statement()
                if stmt:
                    else_body = [stmt]
        
        return IfNode(condition, if_body, else_body)
    
    def parse_do_while(self):
        """do → DO sentencia WHILE LPAREN expresion RPAREN SEMICOLON"""
        self.consume(TokenClassifier.tokens["do"])
        
        # Cuerpo del do-while
        body = []
        if self.match(TokenClassifier.tokens["{"]):
            body = self.parse_block()
        else:
            stmt = self.parse_statement()
            if stmt:
                body = [stmt]
        
        if not self.consume(TokenClassifier.tokens["while"]):
            return None
        
        if not self.consume(TokenClassifier.tokens["("]):
            return None
        
        condition = self.parse_expression()
        if not condition:
            return None
        
        if not self.consume(TokenClassifier.tokens[")"]):
            return None
        
        if not self.consume(TokenClassifier.tokens[";"]):
            return None
        
        return DoWhileNode(body, condition)
    
    def parse_print(self):
        """print → PRINT LPAREN expresion RPAREN SEMICOLON"""
        self.consume(TokenClassifier.tokens["print"])
        
        if not self.consume(TokenClassifier.tokens["("]):
            return None
        
        expression = self.parse_expression()
        if not expression:
            return None
        
        if not self.consume(TokenClassifier.tokens[")"]):
            return None
        
        if not self.consume(TokenClassifier.tokens[";"]):
            return None
        
        return PrintNode(expression)
    
    def parse_for(self):
        """for → FOR LPAREN (expresión | declaración)? SEMICOLON expresion? SEMICOLON (asignacion)? RPAREN sentencia"""
        self.consume(TokenClassifier.tokens["for"])
        
        if not self.consume(TokenClassifier.tokens["("]):
            return None
        
        # Inicialización (declaración o asignación)
        init = None
        if self._is_type_token():
            init = self.parse_declaration()
        elif self.match(TokenClassifier.tokens["IDENTIFIER"]):
            init = self.parse_assignment()
        
        # Condición
        condition = None
        if not self.match(TokenClassifier.tokens[";"]):
            condition = self.parse_expression()

        if not self.consume(TokenClassifier.tokens[";"]):
            return None
        
        # Incremento (asignación)
        increment = None
        if self.match(TokenClassifier.tokens["IDENTIFIER"]):
            increment = self.parse_assignment(required_semicolon=False)

        if not self.consume(TokenClassifier.tokens[")"]):
            return None
        
        # Cuerpo del for
        body = []
        if self.match(TokenClassifier.tokens["{"]):
            body = self.parse_block()
        else:
            stmt = self.parse_statement()
            if stmt:
                body = [stmt]

        #Quitar sólo la variable de control del for del ámbito.

        if init and isinstance(init, DeclarationNode):
            self.symbol_table.remove_variable(init.name)
        
        return ForNode(init, condition, increment, body)
    
    def parse_while(self):
        """while → WHILE LPAREN expresion RPAREN sentencia"""
        self.consume(TokenClassifier.tokens["while"])
        
        if not self.consume(TokenClassifier.tokens["("]):
            return None
        
        condition = self.parse_expression()
        if not condition:
            return None
        
        if not self.consume(TokenClassifier.tokens[")"]):
            return None
        
        # Cuerpo del while
        body = []
        if self.match(TokenClassifier.tokens["{"]):
            body = self.parse_block()
        else:
            stmt = self.parse_statement()
            if stmt:
                body = [stmt]
        
        return WhileNode(condition, body)
    
    def parse_return(self):
        """return → RETURN expresion? SEMICOLON"""
        self.consume(TokenClassifier.tokens["return"])
        
        expression = None
        if not self.match(TokenClassifier.tokens[";"]):
            expression = self.parse_expression()
        
        if not self.consume(TokenClassifier.tokens[";"]):
            return None
        
        return ReturnNode(expression)
    
    def parse_block(self):
        """bloque → LBRACE sentencias* RBRACE"""
        if not self.consume(TokenClassifier.tokens["{"]):
            return []

        self.symbol_table.enter_scope()
        try:
            statements = self._parse_body_until([TokenClassifier.tokens["}"], TokenClassifier.tokens["EOF"]])
            self.consume(TokenClassifier.tokens["}"])
            return statements
        finally:
            self.symbol_table.exit_scope()

    def parse_arguments(self):
        """argumentos → expresion (COMMA expresion)* | epsilon"""
        arguments = []

        if self.match(TokenClassifier.tokens[")"]):
            return arguments

        expression = self.parse_expression()
        if expression is None:
            return arguments
        arguments.append(expression)

        while self.match(TokenClassifier.tokens[","]):
            self.consume(TokenClassifier.tokens[","])
            expression = self.parse_expression()
            if expression is None:
                break
            arguments.append(expression)

        return arguments
    
    # ============ Análisis de expresiones con precedencia ============
    
    def parse_expression(self):
        """expresion → expresion_logica"""
        return self.parse_logical_or()
    
    def parse_logical_or(self):
        """expresion_logica_or → expresion_logica_and (OR expresion_logica_and)*"""
        left = self.parse_logical_and()
        while self.match(TokenClassifier.tokens["||"]):
            self.consume(TokenClassifier.tokens["||"])
            right = self.parse_logical_and()
            left = BinaryOpNode('||', left, right)
        return left
    
    def parse_logical_and(self):
        """expresion_logica_and → expresion_igualdad (AND expresion_igualdad)*"""
        left = self.parse_equality()
        while self.match(TokenClassifier.tokens["&&"]):
            self.consume(TokenClassifier.tokens["&&"])
            right = self.parse_equality()
            left = BinaryOpNode('&&', left, right)
        return left
    
    def parse_equality(self):
        """expresion_igualdad → expresion_relacional ((EQUAL | NOT_EQUAL) expresion_relacional)*"""
        left = self.parse_relational()
        while self.match(TokenClassifier.tokens["=="]) or self.match(TokenClassifier.tokens["!="]):
            if self.match(TokenClassifier.tokens["=="]):
                self.consume(TokenClassifier.tokens["=="])
                operator = '=='
            else:
                self.consume(TokenClassifier.tokens["!="])
                operator = '!='
            right = self.parse_relational()
            left = BinaryOpNode(operator, left, right)
        return left
    
    def parse_relational(self):
        """expresion_relacional → expresion_aditiva ((LESS | GREATER | LESS_EQUAL | GREATER_EQUAL) expresion_aditiva)*"""
        left = self.parse_additive()
        while (self.match(TokenClassifier.tokens["<"]) or self.match(TokenClassifier.tokens[">"]) or
               self.match(TokenClassifier.tokens["<="]) or self.match(TokenClassifier.tokens[">="])):
            if self.match(TokenClassifier.tokens["<"]):
                self.consume(TokenClassifier.tokens["<"])
                operator = '<'
            elif self.match(TokenClassifier.tokens[">"]):
                self.consume(TokenClassifier.tokens[">"])
                operator = '>'
            elif self.match(TokenClassifier.tokens["<="]):
                self.consume(TokenClassifier.tokens["<="])
                operator = '<='
            else:
                self.consume(TokenClassifier.tokens[">="])
                operator = '>='
            right = self.parse_additive()
            left = BinaryOpNode(operator, left, right)
        return left
    
    def parse_additive(self):
        """expresion_aditiva → expresion_multiplicativa ((PLUS | MINUS) expresion_multiplicativa)*"""
        left = self.parse_multiplicative()
        while self.match(TokenClassifier.tokens["+"]) or self.match(TokenClassifier.tokens["-"]):
            if self.match(TokenClassifier.tokens["+"]):
                self.consume(TokenClassifier.tokens["+"])
                operator = '+'
            else:
                self.consume(TokenClassifier.tokens["-"])
                operator = '-'
            right = self.parse_multiplicative()
            left = BinaryOpNode(operator, left, right)
        return left
    
    def parse_multiplicative(self):
        """expresion_multiplicativa → expresion_unaria ((MULTIPLY | DIVIDE | MODULO) expresion_unaria)*"""
        left = self.parse_unary()
        while self.match(TokenClassifier.tokens["*"]) or self.match(TokenClassifier.tokens["/"]) or self.match(TokenClassifier.tokens["%"]):
            if self.match(TokenClassifier.tokens["*"]):
                self.consume(TokenClassifier.tokens["*"])
                operator = '*'
            elif self.match(TokenClassifier.tokens["/"]):
                self.consume(TokenClassifier.tokens["/"])
                operator = '/'
            elif self.match(TokenClassifier.tokens["%"]):
                self.consume(TokenClassifier.tokens["%"])
                operator = '%'

            right = self.parse_unary()
            left = BinaryOpNode(operator, left, right)
        return left
    
    def parse_unary(self):
        """expresion_unaria → (MINUS | NOT) expresion_unaria | expresion_primaria"""
        if self.match(TokenClassifier.tokens["-"]):
            self.consume(TokenClassifier.tokens["-"])
            operand = self.parse_unary()
            return UnaryOpNode('-', operand)
        elif self.match(TokenClassifier.tokens["!"]):
            self.consume(TokenClassifier.tokens["!"])
            operand = self.parse_unary()
            return UnaryOpNode('!', operand)
        return self.parse_primary()
    
    def parse_primary(self):
        """expresion_primaria → NUMBER | IDENTIFIER | LPAREN expresion RPAREN"""
        token = self.current_token()
        if not token:
            return None
        
        if token.type == TokenClassifier.tokens["NUMBER"]:
            self.consume(TokenClassifier.tokens["NUMBER"])
            return NumberNode(token.value)
        
        elif token.type == TokenClassifier.tokens["STRING"]:
            self.consume(TokenClassifier.tokens["STRING"])
            return StringNode(token.value)
        
        elif token.type == TokenClassifier.tokens["IDENTIFIER"]:
            self.consume(TokenClassifier.tokens["IDENTIFIER"])
            if self.match(TokenClassifier.tokens["("]):
                self.consume(TokenClassifier.tokens["("])
                arguments = self.parse_arguments()
                if not self.consume(TokenClassifier.tokens[")"]):
                    return None
                return FunctionCallNode(token.value, arguments)
            if not self._require_declared_variable(token):
                return None
            return IdentifierNode(token.value)
        
        elif token.type == TokenClassifier.tokens["("]:
            self.consume(TokenClassifier.tokens["("])
            expr = self.parse_expression()
            if not self.consume(TokenClassifier.tokens[")"]):
                return None
            return expr
        
        else:
            self.errors.append(f"Expected expression at line {token.line}, column {token.column}")
            return None