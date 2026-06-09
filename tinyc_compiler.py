# tinyc_compiler.py
#!/usr/bin/env python3

import sys
from Lexer.Lexer import Lexer
from abstract_syntax_tree.parser import Parser
from semantic_analysis.semantic_analyzer import SemanticAnalyzer
from semantic_analysis.tac_generator import TACGenerator
from abstract_syntax_tree.optimizer import LocalOptimizer
from vm.vm_codegen import VMCodeGenerator
from codegen.codegen_mips import MIPSGenerator


def compile_file(filename, output_type='vm'):
    with open(filename, 'r') as f:
        source = f.read()
    
    # Fase 1: Léxico
    lexer = Lexer(source)
    tokens, errors = lexer.tokenize()
    
    if errors:
        return False, errors
    
    # Fase 2: Sintáctico
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    if parser.errors:
        return False, parser.errors
    
    # Fase 3: Semántico
    semantic = SemanticAnalyzer()
    errors = semantic.analyze(ast)
    
    if errors:
        return False, errors
    
    # Fase 4: Generación TAC
    tac_gen = TACGenerator()
    tac = tac_gen.generate(ast)
    
    # Fase 5: Optimización
    optimizer = LocalOptimizer()
    optimized_tac = optimizer.optimize(tac)
    
    # Fase 6: Generación de código
    if output_type == 'vm':
        code_gen = VMCodeGenerator()
        output = code_gen.generate(optimized_tac)
    else:
        code_gen = MIPSGenerator()
        output = code_gen.generate(optimized_tac)
    
    return True, output

def main():
    if len(sys.argv) < 2:
        print("Usage: tinyc_compiler.py <file.tc> [--vm | --mips]")
        sys.exit(1)
    
    filename = sys.argv[1]
    output_type = 'vm'
    
    if len(sys.argv) > 2:
        output_type = 'mips' if sys.argv[2] == '--mips' else 'vm'
    
    success, result = compile_file(filename, output_type)
    
    if success:
        print("Compilation successful!")
        if output_type == 'vm':
            # Escribir bytecode
            with open(filename.replace('.tc', '.vm'), 'w') as f:
                for instr in result:
                    f.write(str(instr) + '\n')
            print(f"Bytecode written to {filename.replace('.tc', '.vm')}")
        else:
            # Escribir ensamblador MIPS
            with open(filename.replace('.tc', '.s'), 'w') as f:
                f.write('\n'.join(result))
            print(f"MIPS assembly written to {filename.replace('.tc', '.s')}")
    else:
        print("Compilation failed:")
        for error in result:
            print(f"  {error}")

if __name__ == "__main__":
    main()