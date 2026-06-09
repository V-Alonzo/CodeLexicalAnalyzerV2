# codegen_mips.py

class MIPSGenerator:
    def __init__(self):
        self.code = []
        self.next_temp_reg = 0
        self.temp_location = {}  # temporal -> localización (registro o stack)
    
    def generate(self, tac_instructions):
        """Genera código MIPS a partir de TAC"""
        self._generate_prologue()
        
        for instr in tac_instructions:
            self._generate_instruction(instr)
        
        self._generate_epilogue()
        return self.code
    
    def _generate_prologue(self):
        self.code.append(".text")
        self.code.append(".globl main")
        self.code.append("main:")
        self.code.append("    addiu $sp, $sp, -32")
        self.code.append("    sw $ra, 28($sp)")
        self.code.append("    sw $fp, 24($sp)")
        self.code.append("    move $fp, $sp")
    
    def _generate_epilogue(self):
        self.code.append("    move $sp, $fp")
        self.code.append("    lw $ra, 28($sp)")
        self.code.append("    lw $fp, 24($sp)")
        self.code.append("    addiu $sp, $sp, 32")
        self.code.append("    jr $ra")