# symbol_table.py

class SymbolKind:
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"

class Symbol:
    def __init__(self, name, kind, type_, line=None):
        self.name = name
        self.kind = kind      # variable, function, parameter
        self.type = type_     # int, float, void
        self.line = line
        self.initialized = False
        self.offset = None    # para asignación de memoria

class Scope:
    def __init__(self, name):
        self.name = name       # "global", "function:factorial", "block"
        self.symbols = {}
        self.parent = None
    
    def insert(self, symbol):
        if symbol.name in self.symbols:
            return False  # ya existe
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name):
        return self.symbols.get(name)

class SymbolTable:
    def __init__(self):
        self.scopes = []
        self.enter_scope("global")
    
    def enter_scope(self, name):
        new_scope = Scope(name)
        if self.scopes:
            new_scope.parent = self.scopes[-1]
        self.scopes.append(new_scope)
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def current_scope(self):
        return self.scopes[-1] if self.scopes else None
    
    def insert(self, symbol):
        return self.current_scope().insert(symbol)
    
    def lookup(self, name):
        scope = self.current_scope()
        while scope:
            symbol = scope.lookup(name)
            if symbol:
                return symbol
            scope = scope.parent
        return None
    
    def lookup_current(self, name):
        return self.current_scope().lookup(name)