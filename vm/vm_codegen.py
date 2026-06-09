# vm_codegen.py

class VMCodeGenerator:
    def __init__(self):
        self.instructions = []
    
    def is_imm(self, val):
        val_str = str(val)
        return val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit())
        
    def _load(self, arg, reg):
        """Carga un valor inmediato, string o variable a un registro físico."""
        if self.is_imm(arg):
            self.instructions.append(f"    LOADI {reg}, {arg}")
        elif str(arg).startswith('"'):
            self.instructions.append(f"    LOADSTR {reg}, {arg}")
        else:
            self.instructions.append(f"    LOAD {reg}, {arg}")

    def generate(self, tac_instructions):
        """Convierte TAC a bytecode mediante arquitectura Load-Store"""
        for instr in tac_instructions:
            if instr.op == 'label':
                self.instructions.append(f"{instr.result}:")
                
            elif instr.op == '=':
                self._load(instr.arg1, "R1")
                self.instructions.append(f"    STORE {instr.result}, R1")
                
            elif instr.op in ('+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!='):
                self._load(instr.arg1, "R1")
                self._load(instr.arg2, "R2")
                
                op_map = {
                    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', 
                    '<': 'LT', '>': 'GT', '<=': 'LE', '>=': 'GE', 
                    '==': 'EQ', '!=': 'NEQ'
                }
                
                # Ejecutar y persistir temporal en memoria
                self.instructions.append(f"    {op_map[instr.op]} R3, R1, R2")
                self.instructions.append(f"    STORE {instr.result}, R3")
                
            elif instr.op == 'if':
                self._load(instr.arg1, "R1")
                self.instructions.append(f"    LOADI R2, 0")
                self.instructions.append(f"    CMP R1, R2")
                self.instructions.append(f"    JZ {instr.result}")
                
            elif instr.op == 'goto':
                self.instructions.append(f"    JMP {instr.result}")
                
            elif instr.op == 'return':
                if instr.arg1:
                    self._load(instr.arg1, "R1")
                    self.instructions.append("    RET R1")
                else:
                    self.instructions.append("    RET")
                    
            elif instr.op == 'param':
                self._load(instr.arg1, "R1")
                self.instructions.append("    PUSH_PARAM R1")
                
            elif instr.op == 'pop_param':
                self.instructions.append("    POP_PARAM R1")
                self.instructions.append(f"    STORE {instr.result}, R1")
                
            elif instr.op == 'call':
                if instr.arg1 == 'print':
                    self.instructions.append("    SYSCALL PRINT")
                else:
                    self.instructions.append(f"    CALL {instr.arg1}")
                    # Almacenar el valor de retorno que convencionalmente vive en R1
                    if instr.result:
                        self.instructions.append(f"    STORE {instr.result}, R1")
                        
        return self.instructions