class LocalOptimizer:
    def optimize(self, tac_instructions):
        """Aplica múltiples pases de optimización hasta que el código se estabilice."""
        changed = True
        while changed:
            original_len = len(tac_instructions)
            tac_instructions = self.peephole_optimization(tac_instructions)
            changed = len(tac_instructions) < original_len
            
        return tac_instructions
    
    def peephole_optimization(self, tac_instructions):
        """Elimina copias redundantes. Patrón: tX = Y op Z seguido de Variable = tX"""
        optimized = []
        i = 0
        
        while i < len(tac_instructions):
            instr = tac_instructions[i]
            
            # Verificar si la instrucción genera un temporal
            if instr.result and str(instr.result).startswith('t'):
                if i + 1 < len(tac_instructions):
                    next_instr = tac_instructions[i+1]
                    
                    # Si la siguiente instrucción copia el temporal a una variable real
                    if (next_instr.op == '=' and 
                        next_instr.arg1 == instr.result and 
                        not str(next_instr.result).startswith('t')):
                        
                        # Modificar el destino de la operación original a la variable final
                        instr.result = next_instr.result
                        optimized.append(instr)
                        i += 2  # Consumir ambas instrucciones
                        continue
                        
            optimized.append(instr)
            i += 1
            
        return optimized