# main.py

from Lexer.Lexer import Lexer
from abstract_syntax_tree.parser import Parser
from semantic_analysis.semantic_analyzer import SemanticAnalyzer
from semantic_analysis.tac_generator import TACGenerator

def compile(source_code):
    # Fase 1: Análisis léxico
    lexer = Lexer(source_code)
    tokens, errors = lexer.tokenize()
    
    # Verificar errores léxicos
    lexical_errors = [t for t in errors]
    if lexical_errors:
        return {"success": False, "errors": lexical_errors}
    
    # Fase 2: Análisis sintáctico
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    if parser.errors:
        return {"success": False, "errors": parser.errors}
    
    # Fase 3: Análisis semántico
    semantic = SemanticAnalyzer()
    semantic_errors = semantic.analyze(ast)
    
    if semantic_errors:
        return {"success": False, "errors": semantic_errors}
    
    # Fase 4: Generación de código intermedio
    generator = TACGenerator()
    tac = generator.generate(ast)
    
    return {"success": True, "ast": ast, "tac": tac}

# Ejemplo de uso
if __name__ == "__main__":
    codigo = """
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
    
    result = compile(codigo)
    
    if result["success"]:
        print("Compilación exitosa")
        print("\nCódigo de tres direcciones generado:")
        for i, instr in enumerate(result["tac"]):
            print(f"{i:3}: {instr}")
    else:
        print("Errores encontrados:")
        for error in result["errors"]:
            print(f"  {error}")