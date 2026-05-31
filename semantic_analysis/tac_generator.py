# tac_generator.py

from abstract_syntax_tree.parser import ReturnNode
class TACInstruction:
    def __init__(self, op, arg1=None, arg2=None, result=None):
        self.op = op          # '+', '-', '*', '/', '=', 'if', 'goto', 'label', 'param', 'call', 'return'
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __repr__(self):
        if self.op == 'label':
            return f"{self.result}:"
        elif self.op == 'if':
            return f"if {self.arg1} {self.arg2} goto {self.result}"
        elif self.op == 'goto':
            return f"goto {self.result}"
        elif self.op == '=':
            return f"{self.result} = {self.arg1}"
        elif self.op == 'return':
            return f"return {self.arg1}" if self.arg1 else "return"
        elif self.op == 'param':
            return f"param {self.arg1}"
        elif self.op == 'call':
            return f"{self.result} = call {self.arg1}, {self.arg2}"
        else:
            return f"{self.result} = {self.arg1} {self.op} {self.arg2}"

class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def add(self, instruction):
        self.instructions.append(instruction)
    
    def generate(self, ast):
        self.visit(ast)
        return self.instructions
    
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        # Por defecto, no genera código
        return None
    
    def visit_Program(self, node):
        for func in node.functions:
            self.visit(func)

    def visit_FunctionCallNode(self, node):
        # Generar código para los argumentos
        arg_temps = []
        for arg in node.arguments:
            arg_temp = self.visit(arg)
            arg_temps.append(arg_temp)
            self.add(TACInstruction('param', arg_temp))
        
        # Llamada a la función
        result = self.new_temp()
        self.add(TACInstruction('call', node.name, str(len(node.arguments)), result))
        return result
    
    def visit_FunctionNode(self, node):
        # Etiqueta de entrada de la función
        self.add(TACInstruction('label', result=node.name))
        
        # Generar código para el cuerpo
        for stmt in node.body:
            # La función principal no crea temp para su return
            if isinstance(stmt, ReturnNode) and node.name == "main":
                self.visit_ReturnNode(stmt, should_create_temp=False)
            else:
                self.visit(stmt)
        
        # Return implícito si no hay
        if not any(isinstance(stmt, ReturnNode) for stmt in node.body):
            self.add(TACInstruction('return'))
    
    def visit_DeclarationNode(self, node):
        # Si tiene inicializador, generar código para asignación
        if node.initializer:
            temp = self.visit(node.initializer)
            self.add(TACInstruction('=', temp, result=node.name))
    
    def visit_AssignmentNode(self, node):
        temp = self.visit(node.expression)

        if  temp:
            self.add(TACInstruction('=', temp, result=node.name))
    
    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        result = self.new_temp()
        self.add(TACInstruction(node.operator, left, right, result))
        return result
    
    def visit_NumberNode(self, node):
        result = self.new_temp()
        self.add(TACInstruction('=', str(node.value), result=result))
        return result
    
    def visit_IdentifierNode(self, node):
        result = self.new_temp()
        self.add(TACInstruction('=', node.name, result=result))
        return result
    
    def visit_IfNode(self, node):
        # Generar código para la condición
        cond_temp = self.visit(node.condition)
        
        # Etiquetas para else y end
        else_label = self.new_label()
        end_label = self.new_label()
        
        # Salto condicional
        # Asumimos que la condición es verdadera si es != 0
        self.add(TACInstruction('if', cond_temp, '== 0', else_label))
        
        # Cuerpo del if
        for stmt in node.if_body:
            self.visit(stmt)
        
        # Salto al final
        self.add(TACInstruction('goto', result=end_label))
        
        # Etiqueta del else
        self.add(TACInstruction('label', result=else_label))
        
        # Cuerpo del else (si existe)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        # Etiqueta final
        self.add(TACInstruction('label', result=end_label))
    
    def visit_WhileNode(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Etiqueta de inicio del bucle
        self.add(TACInstruction('label', result=start_label))
        
        # Generar condición
        cond_temp = self.visit(node.condition)
        self.add(TACInstruction('if', cond_temp, '== 0', end_label))
        
        # Cuerpo del while
        for stmt in node.body:
            self.visit(stmt)
        
        # Volver al inicio
        self.add(TACInstruction('goto', result=start_label))
        
        # Etiqueta de salida
        self.add(TACInstruction('label', result=end_label))
    
    def visit_ReturnNode(self, node, should_create_temp=True):
        if node.expression:
            if should_create_temp:
                temp = self.visit(node.expression)
                self.add(TACInstruction('return', temp))
            else:
                self.add(TACInstruction('return', str(node.expression.value)))

        else:
            self.add(TACInstruction('return'))
    
    def visit_PrintNode(self, node):
        # Implementación simplificada: tratar print como función de biblioteca
        temp = self.visit(node.expression)
        self.add(TACInstruction('param', temp))
        self.add(TACInstruction('call', 'print', '1', '?'))  # No se usa el resultado