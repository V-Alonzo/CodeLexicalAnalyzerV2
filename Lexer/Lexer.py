# lexer_basico.py
import re
from typing import List, Tuple, Optional

# Definimos los tipos de token como constantes
class TokenClassifier:

    tokens = {
        #Palabras reservadas
        "if" : "IF",
        "else" : "ELSE",
        "while" : "WHILE",
        "return" : "RETURN",
        "int" : "INT",
        "float" : "FLOAT",

        # Identificadores y literales
        "IDENTIFIER" : 'IDENTIFIER',
        "NUMBER" : 'NUMBER',
        "STRING" : 'STRING',

        # Operadores
        "+" : 'PLUS',           # '+'
        "-" : 'MINUS',         # '-'
        "*" : 'MULTIPLY',   # '*'
        "/" : 'DIVIDE',       # '/'
        "=" : 'ASSIGN',       # '='
        "==" : 'EQUAL',         # '=='
        "<" : 'LESS',           # '<'
        ">" : 'GREATER',     # '>'
        ">=" : 'GREATER_EQUAL', # '>='
        "<=" : 'LESS_EQUAL',       # '<='
        "!=" : 'NOT_EQUAL',         # '!='


        # Delimitadores
        "(" : 'LPAREN',       # '('
        ")" : 'RPAREN',       # ')'
        "{" : 'LBRACE',       # '{'
        "}" : 'RBRACE',       # '}'
        ";" : 'SEMICOLON', # ';'
        "," : 'COMMA',         # ','

        # Lógicos
        "&&" : "AND", # '&&'
        "||" : "OR",   # '||'
        "!" : "NOT", # '!'

        # Especiales
        "ERROR" : 'ERROR',
        "EOF" : 'EOF',

        # Hex number
        "HEX_NUMBER" : 'HEX_NUMBER',

    }

    delimiters = {
        "(" : 'LPAREN',       # '('
        ")" : 'RPAREN',       # ')'
        "{" : 'LBRACE',       # '{'
        "}" : 'RBRACE',       # '}'
        ";" : 'SEMICOLON', # ';'
        "," : 'COMMA',         # ','
    }


class Token:
    def __init__(self, type_: str, value: any, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.errors: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Retorna el carácter actual o None si es EOF"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def advance(self):
        """Avanza una posición"""
        if self.current_char() == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def peek(self) -> Optional[str]:
        """Observa el siguiente carácter sin consumirlo"""
        peek_pos = self.position + 1
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def skip_whitespace(self):
        """Salta espacios, tabs y nuevas líneas"""
        while self.current_char() and self.current_char().isspace():
            self.advance()        
    
    def read_number(self) -> Token:
        """Lee un número (entero, real o hexadecimal)"""
        start_pos = self.position
        start_col = self.column
        is_float = False
        
        # Leer parte entera
        if self.current_char() == '0' and self.peek() in 'xX':
            # Número hexadecimal
            self.advance()  # Consumir '0' y pasar al siguiente caracter.
            self.advance()  # Consumir 'x' o 'X' y pasar al siguiente caracter.

            while self.current_char() and (self.current_char().isdigit() or self.current_char().lower() in 'abcdef'):
                self.advance()

            if self.current_char() and not self.current_char().isspace() and not self.current_char() in TokenClassifier.delimiters:
                while self.current_char() and not self.current_char().isspace() and not self.current_char() in TokenClassifier.delimiters:
                    self.advance()

                return Token(TokenClassifier.tokens["ERROR"], f"Invalid hexadecimal number: {self.source[start_pos:self.position]}", self.line, start_col)

            number_str = self.source[start_pos:self.position]
            try:
                value = int(number_str, 16)
            except ValueError:
                return Token(TokenClassifier.tokens["ERROR"], f"Invalid hexadecimal number: {number_str}", self.line, start_col)
            
            return Token(TokenClassifier.tokens["HEX_NUMBER"], (number_str, value), self.line, start_col)
        else:
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        # Verificar si tiene parte decimal
        if self.current_char() == '.' and self.peek() and self.peek().isdigit():
            is_float = True
            self.advance()  # Consumir el punto
            # Leer parte decimal
            while self.current_char() and self.current_char().isdigit():
                self.advance()
        
        number_str = self.source[start_pos:self.position]
        value = float(number_str) if is_float else int(number_str)
        
        return Token(TokenClassifier.tokens["NUMBER"], value, self.line, start_col)
    
    def read_identifier(self) -> Token:
        """Lee un identificador o palabra reservada"""
        start_pos = self.position
        start_col = self.column
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        
        identifier = self.source[start_pos:self.position]
        
        # Verificar si es palabra reservada
        token_type = TokenClassifier.tokens[identifier] if identifier in TokenClassifier.tokens else TokenClassifier.tokens["IDENTIFIER"]
        
        return Token(token_type, identifier, self.line, start_col)
    
    def read_string(self) -> Token:
        """Lee una cadena entre comillas dobles"""
        start_pos = self.position
        start_col = self.column
        self.advance()  # Consumir la comilla de apertura
        
        string_value = ""
        while self.current_char() and self.current_char() != '"':
            string_value += self.current_char()
            self.advance()
        
        if self.current_char() == '"':
            self.advance()  # Consumir la comilla de cierre
            return Token(TokenClassifier.tokens["STRING"], string_value, self.line, start_col)
        else:
            return Token(TokenClassifier.tokens["ERROR"], "Unterminated string", self.line, start_col)
    
    def get_next_token(self) -> Optional[Token]:
        """Obtiene el siguiente token del código fuente"""
        self.skip_whitespace()
        
        char = self.current_char()

        if char is None:
            return Token(TokenClassifier.tokens["EOF"], None, self.line, self.column)
        
        # Números
        if char.isdigit():
            return self.read_number()
        
        # Identificadores y palabras clave
        if char.isalpha() or char == '_':
            return self.read_identifier()
        
        # Cadenas
        if char == '"':
            return self.read_string()
        
        # Operadores y símbolos individuales
        start_col = self.column
            
        next_char = self.peek()

        if next_char == None:
            self.advance()
            return Token(TokenClassifier.tokens[char], char, self.line, start_col) if char in TokenClassifier.tokens else Token(TokenClassifier.tokens["ERROR"], f"Carácter desconocido: '{char}'", self.line, start_col)
        
        # Verificar si es un operador de dos caracteres (&&, ||, ==, !=, <=, >=)
        combined_token = char + next_char

        if combined_token in TokenClassifier.tokens:
            self.advance()  # Consumir el segundo carácter
            self.advance()
            return Token(TokenClassifier.tokens[combined_token], combined_token, self.line, start_col)
        
        self.advance() 
        return Token(TokenClassifier.tokens[char], char, self.line, start_col) if char in TokenClassifier.tokens else Token(TokenClassifier.tokens["ERROR"], f"Carácter desconocido: '{char}'", self.line, start_col)
        
    
    def tokenize(self) -> List[Token]:
        """Convierte todo el código fuente en una lista de tokens"""
        self.tokens = []
        self.errors = []

        while True:

            token = self.get_next_token()
            self.tokens.append(token)
            if token.type == TokenClassifier.tokens["ERROR"]:
                self.errors.append(token)
            if token.type == TokenClassifier.tokens["EOF"]:
                break

        return self.tokens, self.errors
    
    def get_results(self):
        if not self.tokens:
            self.tokenize()

        ans = f"""

{"=" * 60}
CÓDIGO FUENTE:

{self.source}
{"=" * 60}
ANÁLISIS LÉXICO:
{"-" * 60}
"""

        for token in self.tokens:
            ans += f"{token}\n"

        ans += f"""

{"=" * 60}

REPORTE DE ERRORES:
{"-" * 60}

"""
        
        for error in self.errors:
            ans += f"{error}\n"

        return ans


if __name__ == "__main__":

    codigo_ejemplo = """
    if (! (a != 0xFkF) && b <= 0xA3 || c >= 0x10) {}
    """
    
    print("=" * 60)
    print("CÓDIGO FUENTE:")
    print(codigo_ejemplo)
    print("=" * 60)
    print("\nANÁLISIS LÉXICO:")
    print("-" * 60)
    
    lexer = Lexer(codigo_ejemplo)
    tokens, errors = lexer.tokenize()
    
    for token in tokens:
        print(token)