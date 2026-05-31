# semantic_analyzer.py

from semantic_analysis.symbol_table import SymbolTable, Symbol, SymbolKind
from abstract_syntax_tree.parser import ASTNode

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function = None
    
    def analyze(self, ast):
        self.visit(ast)
        return self.errors
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        # Por defecto, visitar todos los atributos que sean nodos o listas
        for attr_name in dir(node):
            attr = getattr(node, attr_name)
            if isinstance(attr, ASTNode):
                self.visit(attr)
            elif isinstance(attr, list):
                for item in attr:
                    if isinstance(item, ASTNode):
                        self.visit(item)
    
    def visit_Program(self, node):
        for func in node.functions:
            self.visit(func)
    
    def visit_FunctionNode(self, node):
        # Verificar que la función no esté redeclarada
        existing = self.symbol_table.lookup_current(node.name)
        if existing:
            self.errors.append(f"Line {node.line}: function '{node.name}' already declared")
            return
        
        # Registrar la función en la tabla de símbolos
        func_symbol = Symbol(node.name, SymbolKind.FUNCTION, node.return_type)
        self.symbol_table.insert(func_symbol)
        
        # Entrar al ámbito de la función
        self.symbol_table.enter_scope(f"function:{node.name}")
        self.current_function = node
        
        # Registrar parámetros en el ámbito
        for param_type, param_name in node.parameters:
            param_symbol = Symbol(param_name, SymbolKind.PARAMETER, param_type)
            param_symbol.initialized = True
            if not self.symbol_table.insert(param_symbol):
                self.errors.append(f"Line {node.line}: parameter '{param_name}' already defined")
        
        # Analizar el cuerpo (declaraciones y sentencias)
        for stmt in node.body:
            self.visit(stmt)
        
        # Verificar que la función retorne un valor si no es void
        # (por simplicidad, omitir esta verificación en la práctica inicial)
        
        self.symbol_table.exit_scope()
        self.current_function = None
    
    def visit_DeclarationNode(self, node):
        # Verificar que no exista otra variable con el mismo nombre en el ámbito actual
        existing = self.symbol_table.lookup_current(node.name)
        if existing:
            self.errors.append(f"Line {node.line}: variable '{node.name}' already declared in this scope")
            return
        
        # Registrar la variable
        var_symbol = Symbol(node.name, SymbolKind.VARIABLE, node.var_type)
        if node.initializer:
            var_symbol.initialized = True
            # Verificar tipo del inicializador
            # (se implementa en la verificación de tipos)
        
        self.symbol_table.insert(var_symbol)
        
        # Analizar el inicializador si existe
        if node.initializer:
            self.visit(node.initializer)
    
    def visit_AssignmentNode(self, node):
        # Verificar que la variable esté declarada
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.append(f"Line {node.line}: variable '{node.name}' is not declared")
        else:
            symbol.initialized = True
        
        # Analizar la expresión del lado derecho
        self.visit(node.expression)
    
    def visit_IdentifierNode(self, node):
        # Verificar que el identificador esté declarado
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self.errors.append(f"Line {node.line}: variable '{node.name}' is not declared")
        else:
            # Almacenar el tipo en el nodo para uso posterior
            node.symbol = symbol
    
    def visit_BinaryOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Aquí se podría verificar compatibilidad de tipos
    
    def visit_NumberNode(self, node):
        pass  # No hay validación semántica adicional
    
    # Métodos similares para otros tipos de nodos...