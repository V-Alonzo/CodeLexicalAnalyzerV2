# vm_interpreter.py
import sys
import re

class VirtualMachine:
    def __init__(self, bytecode, labels=None):
        self.bytecode = bytecode
        self.labels = labels or {}

        self.registers = [0] * 16
        self.frames = [{}]

        # Comenzar en main
        self.pc = self.labels.get("main", 0)

        self.stack = []
        self.param_stack = []
        self.running = True

        self.last_cmp = 0
        
    def get_memory_addr(self, identifier):
        if isinstance(identifier, int): return identifier
        if identifier not in self.var_map:
            self.var_map[identifier] = self.next_addr
            self.next_addr += 1
        return self.var_map[identifier]

    def run(self):
        while self.running and self.pc < len(self.bytecode):
            instr = self.bytecode[self.pc]
            self.execute(instr)
            self.pc += 1

    def execute(self, instr):
        opcode = instr[0]
        
        if opcode == 'LOAD':
            self.registers[instr[1]] = self.load_var(instr[2])
        elif opcode == 'LOADI':
            self.registers[instr[1]] = instr[2]
        elif opcode == 'LOADSTR':
            self.registers[instr[1]] = instr[2]
        elif opcode == 'STORE':
            self.store_var(
                instr[1],
                self.registers[instr[2]]
            )
        
        # Operaciones Matemáticas
        elif opcode == 'ADD':
            self.registers[instr[1]] = self.registers[instr[2]] + self.registers[instr[3]]
        elif opcode == 'SUB':
            self.registers[instr[1]] = self.registers[instr[2]] - self.registers[instr[3]]
        elif opcode == 'MUL':
            self.registers[instr[1]] = self.registers[instr[2]] * self.registers[instr[3]]
        elif opcode == 'DIV':
            self.registers[instr[1]] = self.registers[instr[2]] // self.registers[instr[3]]
        
        # Operaciones Relacionales (Asignan 1 ó 0)
        elif opcode == 'LT':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] < self.registers[instr[3]] else 0
        elif opcode == 'GT':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] > self.registers[instr[3]] else 0
        elif opcode == 'LE':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] <= self.registers[instr[3]] else 0
        elif opcode == 'GE':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] >= self.registers[instr[3]] else 0
        elif opcode == 'EQ':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] == self.registers[instr[3]] else 0
        elif opcode == 'NEQ':
            self.registers[instr[1]] = 1 if self.registers[instr[2]] != self.registers[instr[3]] else 0
        
        # Lógica de Salto
        elif opcode == 'CMP':
            self.last_cmp = self.registers[instr[1]] - self.registers[instr[2]]
        elif opcode == 'JMP':
            self.pc = instr[1] - 1
        elif opcode == 'JZ':
            if self.last_cmp == 0: self.pc = instr[1] - 1
        elif opcode == 'JNZ':
            if self.last_cmp != 0: self.pc = instr[1] - 1
            
        # Funciones y Pasos de Entorno
        elif opcode == 'PUSH_PARAM':
            self.param_stack.append(self.registers[instr[1]])
        elif opcode == 'POP_PARAM':
            self.registers[instr[1]] = self.param_stack.pop()
        elif opcode == 'CALL':
            self.frames.append({})

            self.stack.append(self.pc)

            self.pc = instr[1] - 1
        elif opcode == 'RET':

            return_value = None

            if len(instr) > 1:
                return_value = self.registers[instr[1]]

            if len(self.frames) > 1:
                self.frames.pop()

            if return_value is not None:
                self.registers[1] = return_value

            if self.stack:
                self.pc = self.stack.pop()
            else:
                self.running = False           
        # Interrupciones
        elif opcode == 'SYSCALL':
            if instr[1] == 'PRINT':
                val = self.param_stack.pop()
                if isinstance(val, str):
                    val = val.replace('\\n', '\n')
                    print(val.strip('"'), end='')
                else:
                    print(val, end='')
        elif opcode == 'HALT':
            self.running = False

    def store_var(self, name, value):
        self.frames[-1][name] = value

    def load_var(self, name):
        for frame in reversed(self.frames):
            if name in frame:
                return frame[name]

        return 0
    
def read_bytecode_from_file(filename):
    bytecode = []
    labels = {}

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.endswith(':'):
                labels[line[:-1]] = len(bytecode)
            else:
                parts = re.findall(r'".*?"|\S+', line)

                opcode = parts[0]
                args = []

                for arg in parts[1:]:
                    if arg.startswith('"'):
                        args.append(arg)
                    else:
                        arg = arg.rstrip(',')

                        if arg.startswith('R') and arg[1:].isdigit():
                            args.append(int(arg[1:]))
                        elif arg.isdigit() or (arg.startswith('-') and arg[1:].isdigit()):
                            args.append(int(arg))
                        else:
                            args.append(arg)

                bytecode.append((opcode,) + tuple(args))

    resolved_bytecode = []

    for instr in bytecode:
        resolved_args = [
            labels.get(arg, arg) if isinstance(arg, str) else arg
            for arg in instr[1:]
        ]
        resolved_bytecode.append((instr[0],) + tuple(resolved_args))

    return resolved_bytecode, labels

if __name__ == "__main__":
    
    # Ejemplo de uso:
    # Programa ejemplo: calcular 5 + 3
    # bytecode = [
    #     ('LOADI', 1, 5),   # R1 = 5
    #     ('LOADI', 2, 3),   # R2 = 3
    #     ('ADD', 3, 1, 2),  # R3 = R1 + R2
    #     ('HALT',)
    # ]
    
    if len(sys.argv) < 2:
        print("Usage: vm_interpreter.py <file.vm>")
        sys.exit(1)

    bytecode, labels = read_bytecode_from_file(sys.argv[1])

    vm = VirtualMachine(bytecode, labels)
    vm.run()