# main.py
import sys
from Lexer.Lexer import Lexer
from abstract_syntax_tree.parser import Parser
from abstract_syntax_tree.ast_nodes import *
from abstract_syntax_tree.semantic_analyzer import SemanticAnalyzer

def print_ast(node, indent=0):
    """Imprime el AST de forma legible"""
    indent_str = "  " * indent
    if isinstance(node, Program):
        print(f"{indent_str}Program")
        for func in node.functions:
            print_ast(func, indent + 1)
    elif hasattr(node, 'to_dict'):
        import json
        print(json.dumps(node.to_dict(), indent=2))
    else:
        print(f"{indent_str}{repr(node)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Leer el archivo fuente
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    # Análisis léxico
    print("=" * 60)
    print("LEXICAL ANALYSIS")
    print("=" * 60)
    
    lexer = Lexer(source_code)
    tokens, errors = lexer.tokenize()
    
    # Mostrar tokens generados
    for token in tokens:
        if token.type != 'EOF':
            print(f"  {token}")
    
    # Verificar errores léxicos
    if len(errors) > 0:
        print("\n" + "=" * 60)
        print("LEXICAL ERRORS FOUND")
        print("=" * 60)
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    
    # Análisis sintáctico
    print("\n" + "=" * 60)
    print("SYNTAX ANALYSIS")
    print("=" * 60)
    
    parser = Parser(tokens)
    ast = parser.parse_program()

    if parser.errors:
        print("SYNTAX ERRORS FOUND:")
        for error in parser.errors:
            print(f"  {error}")
        sys.exit(1)

    semantic_analyzer = SemanticAnalyzer()
    semantic_errors = semantic_analyzer.analyze(ast)
    if semantic_errors:
        print("SEMANTIC ERRORS FOUND:")
        for error in semantic_errors:
            print(f"  {error}")
        sys.exit(1)
    
    print("Parsing successful!")
    print("\n" + "=" * 60)
    print("ABSTRACT SYNTAX TREE (AST)")
    print("=" * 60)
    print_ast(ast)

if __name__ == "__main__":
    main()