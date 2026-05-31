class SymbolTable:

    def __init__(self):
        self.scopes = [{}]  # Pila de diccionarios para manejar ámbitos anidados
    
    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("No se puede salir del ámbito global")
    
    def declare(self, name, type):
        if name in self.scopes[-1]:
            raise Exception(f"Variable '{name}' ya declarada en este ámbito")
        self.scopes[-1][name] = type

    def lookup_current_scope(self, name):
        return self.scopes[-1].get(name)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def remove_variable(self, name):
        if name in self.scopes[-1]:
            del self.scopes[-1][name]