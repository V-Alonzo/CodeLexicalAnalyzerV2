# ast_nodes.py

class ASTNode:
    """Clase base para todos los nodos del AST"""
    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column
    
    def __repr__(self):
        return self.__class__.__name__
    
    def to_dict(self):
        """Convierte el nodo a diccionario para depuración"""
        return {"type": self.__class__.__name__}


class Program(ASTNode):
    """Nodo raíz del programa"""
    def __init__(self, functions):
        super().__init__()
        self.functions = functions   # lista de FunctionNode
    
    def to_dict(self):
        return {
            "type": "Program",
            "functions": [f.to_dict() for f in self.functions]
        }
    

class StringNode(ASTNode):
    """Literal de cadena"""
    def __init__(self, value):
        super().__init__()
        self.value = value   # string
    
    def to_dict(self):
        return {"type": "String", "value": self.value}
        


class FunctionNode(ASTNode):
    """Declaración de función"""
    def __init__(self, return_type, name, parameters, body):
        super().__init__()
        self.return_type = return_type   # 'int', 'float', 'void'
        self.name = name                 # string
        self.parameters = parameters     # lista de (type, name)
        self.body = body                 # lista de StatementNode
    
    def to_dict(self):
        return {
            "type": "Function",
            "return_type": self.return_type,
            "name": self.name,
            "parameters": [{"type": p[0], "name": p[1]} for p in self.parameters],
            "body": [s.to_dict() for s in self.body]
        }


class DeclarationNode(ASTNode):
    """Declaración de variable"""
    def __init__(self, var_type, name, initializer=None):
        super().__init__()
        self.var_type = var_type     # 'int', 'float' o 'string
        self.name = name             # string
        self.initializer = initializer  # ExpressionNode o None
    
    def to_dict(self):
        result = {"type": "Declaration", "var_type": self.var_type, "name": self.name}
        if self.initializer:
            result["initializer"] = self.initializer.to_dict()
        return result


class AssignmentNode(ASTNode):
    """Asignación de variable"""
    def __init__(self, name, expression):
        super().__init__()
        self.name = name
        self.expression = expression
    
    def to_dict(self):
        return {
            "type": "Assignment",
            "name": self.name,
            "expression": self.expression.to_dict()
        }


class IfNode(ASTNode):
    """Sentencia if-else"""
    def __init__(self, condition, if_body, else_body=None):
        super().__init__()
        self.condition = condition
        self.if_body = if_body       # lista de StatementNode
        self.else_body = else_body   # lista de StatementNode o None
    
    def to_dict(self):
        result = {
            "type": "If",
            "condition": self.condition.to_dict(),
            "if_body": [s.to_dict() for s in self.if_body]
        }
        if self.else_body:
            result["else_body"] = [s.to_dict() for s in self.else_body]
        return result

class ForNode(ASTNode):
    """Sentencia for"""
    def __init__(self, initializer, condition, increment, body):
        super().__init__()
        self.initializer = initializer  # StatementNode
        self.condition = condition      # ExpressionNode
        self.increment = increment      # StatementNode
        self.body = body                # lista de StatementNode
    
    def to_dict(self):
        return {
            "type": "For",
            "initializer": self.initializer.to_dict(),
            "condition": self.condition.to_dict(),
            "increment": self.increment.to_dict(),
            "body": [s.to_dict() for s in self.body]
        }

class WhileNode(ASTNode):
    """Sentencia while"""
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body             # lista de StatementNode
    
    def to_dict(self):
        return {
            "type": "While",
            "condition": self.condition.to_dict(),
            "body": [s.to_dict() for s in self.body]
        }
    
class DoWhileNode(ASTNode):
    """Sentencia do-while"""
    def __init__(self, body, condition):
        super().__init__()
        self.body = body             # lista de StatementNode
        self.condition = condition
    
    def to_dict(self):
        return {
            "type": "DoWhile",
            "body": [s.to_dict() for s in self.body],
            "condition": self.condition.to_dict()
        }


class ReturnNode(ASTNode):
    """Sentencia return"""
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
    
    def to_dict(self):
        return {
            "type": "Return",
            "expression": self.expression.to_dict() if self.expression else None
        }


class PrintNode(ASTNode):
    """Sentencia print incorporada"""
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
    
    def to_dict(self):
        return {
            "type": "Print",
            "expression": self.expression.to_dict()
        }


class BinaryOpNode(ASTNode):
    """Operación binaria"""
    def __init__(self, operator, left, right):
        super().__init__()
        self.operator = operator   # '+', '-', '*', '/', '<', '>', '==', '!=', etc.
        self.left = left
        self.right = right
    
    def to_dict(self):
        return {
            "type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class UnaryOpNode(ASTNode):
    """Operación unaria"""
    def __init__(self, operator, operand):
        super().__init__()
        self.operator = operator   # '-', '!'
        self.operand = operand
    
    def to_dict(self):
        return {
            "type": "UnaryOp",
            "operator": self.operator,
            "operand": self.operand.to_dict()
        }


class NumberNode(ASTNode):
    """Literal numérico (entero o flotante)"""
    def __init__(self, value):
        super().__init__()
        self.value = value   # int o float
    
    def to_dict(self):
        return {"type": "Number", "value": self.value}


class IdentifierNode(ASTNode):
    """Referencia a variable"""
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def to_dict(self):
        return {"type": "Identifier", "name": self.name}


class FunctionCallNode(ASTNode):
    """Llamada a función"""
    def __init__(self, name, arguments):
        super().__init__()
        self.name = name
        self.arguments = arguments

    def to_dict(self):
        return {
            "type": "FunctionCall",
            "name": self.name,
            "arguments": [argument.to_dict() for argument in self.arguments],
        }