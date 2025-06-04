"""
🧩 RESOLUTOR KAKURO CSP - GOOGLE COLAB
====================================

Implementación de Problema de Satisfacción de Restricciones (CSP) 
con Backtracking Cronológico para resolver puzzles Kakuro.

TÉCNICAS CSP IMPLEMENTADAS:
- Backtracking Cronológico
- Propagación de Restricciones  
- Forward Checking
- Consistencia de Arco
- Heurísticas de Ordenamiento
- Detección Temprana de Conflictos

Para usar en Colab:
1. Ejecuta todo el código
2. Llama a solve_kakuro_colab() 
3. Sube tu archivo de puzzle
4. ¡Disfruta la solución!
"""

import math
import sys
import logging
import hashlib
import os
from google.colab import files
import io

def get_sums(target, count):
    """Genera todas las combinaciones posibles que suman al objetivo"""
    if count == 2:
        sums = [
            [target - x, x] for x in range(1, target - 1)
            if target - x != x and x < 10 and (target - x) < 10
        ]
    else:
        sums = []
        for x in range(1, target - 1):
            sums.extend(
                [sum + [x] for sum in get_sums(target - x, count - 1) 
                 if x not in sum and x < 10]
            )
    return sums

def get_unique_sums(target, count):
    """Retorna combinaciones únicas eliminando permutaciones redundantes"""
    sums = get_sums(target, count)
    unique_sums = set()
    for sum in sums:
        unique_sums.add(tuple(sorted(sum)))
    return list(unique_sums)

def combinations(nums):
    """Genera todas las permutaciones para backtracking"""
    combos = []
    if len(nums) == 2:
        return [[nums[0], nums[1]], [nums[1], nums[0]]]
    else:
        for num in nums:
            nums2 = nums[:]
            nums2.remove(num)
            combos.extend([x + [num] for x in combinations(nums2)])
    return combos

class Run(object):
    """Representa una restricción individual del CSP"""
    coord_changes = []
    h_guess_coords = {}
    v_guess_coords = {}
    min_remaining = 0

    def __init__(self, total, length, start, vert, solver):
        self.solver = solver
        self.length = length
        self.total = total
        self.intersect = solver.horizontal_runs if vert else solver.vertical_runs
        self.__class__.min_remaining = len(solver.horizontal_runs)
        self.sequences = get_unique_sums(total, length)
        if len(self.sequences) == 0:
            raise Exception("Error: no se encontraron secuencias válidas")
        self.digit_coords = {x: set() for x in range(1, 10)}
        (a, b) = (0, 1) if vert else (1, 0)
        self.coords = [(start[0] + a * x, start[1] + b * x) for x in range(length)]

    def get_digits(self):
        """Calcula el dominio disponible para variables en esta restricción"""
        found_digits = set(self._get_found())
        all_digits = set()
        required_digits = set(self.sequences[0])
        
        for sequence in self.sequences:
            if found_digits.issubset(set(sequence)) or len(found_digits) == 0:
                all_digits = all_digits | set(sequence)
                required_digits = required_digits & set(sequence)
        
        all_digits = all_digits - found_digits
        required_digits = required_digits - found_digits
        return all_digits, required_digits

    def _get_found(self):
        """Obtener dígitos ya asignados"""
        found_digits = []
        for coord in self.coords:
            if coord in self.solver.solution:
                found_digits.append(self.solver.solution[coord])
        return found_digits

    def undo(self, guess_coord):
        """Operación de backtracking"""
        coord = None
        while coord != guess_coord:
            coord = self.coord_changes.pop()
            value = self.solver.solution[coord]
            del self.solver.solution[coord]

    def add_found(self, coord, found, testing=False):
        """Agregar nueva asignación"""
        self.solver.solution[coord] = found
        if not testing:
            if coord in self.h_guess_coords:
                del self.h_guess_coords[coord]
            if coord in self.v_guess_coords:
                del self.v_guess_coords[coord]
        self.coord_changes.append(coord)

    def test_possibilities(self, limit):
        """Backtracking controlado"""
        all_, required = self.get_digits()
        combos = []
        
        if len(all_) == len(required) and len(all_) > 0:
            combos = combinations(list(required))
        else:
            remaining = self.total
            length = self.length
            for coord in self.coords:
                if coord in self.solver.solution:
                    remaining -= self.solver.solution[coord]
                    length -= 1
            if length == 2:
                sub_sequences = get_unique_sums(remaining, length)
                combos.extend(get_sums(remaining, length))
        
        if len(combos) <= limit and len(combos) != 0:
            self._test(combos)
        return (len(combos) <= limit)

    def _fill_unique(self, required_digits):
        """Llenar variables con dominio único"""
        count = 0
        for digit, coords in self.digit_coords.items():
            if len(coords) == 1 and digit in required_digits:
                coord = coords.pop()
                if coord not in self.solver.solution:
                    count += 1
                    self.add_found(coord, digit)
        return count

    def fill_cells(self, test=False):
        """Propagación de restricciones"""
        self.digit_coords = {x: set() for x in range(1, 10)}
        found = self._get_found()
        
        if len(found) != len(set(found)):
            return -1
        
        digits1, digits2 = self.get_digits()
        filled_count = 0
        
        for coord in self.coords:
            if coord not in self.solver.solution:
                digits3, digits4 = self.intersect[coord].get_digits()
                common = digits3 & digits1
                
                if len(common) == 1:
                    found = common.pop()
                    self.add_found(coord, found, test)
                    if found in digits2:
                        digits2.remove(found)
                    filled_count += 1
                elif len(common) == 0:
                    return -1
                
                for digit in common:
                    self.digit_coords[digit].add(coord)
                
                if test and filled_count != 0 and self.intersect[coord].fill_cells(test) == -1:
                    return -1
        
        filled_count += self._fill_unique(digits2)
        return filled_count

    def _test(self, value_set):
        """Backtracking cronológico"""
        valid = []
        for values in value_set:
            idx = 0
            eliminated = False
            test_coords = []
            
            for run_coord in self.coords:
                if run_coord not in self.solver.solution:
                    test_coords.append(run_coord)
                    self.add_found(run_coord, values[idx])
                    idx += 1
            
            for test_coord in test_coords:
                if self.intersect[test_coord].fill_cells(True) == -1:
                    eliminated = True
                    break
            
            if not eliminated:
                valid.append(values)
            
            if len(self.intersect) == len(self.solver.solution):
                self.solver.add_solution()
                self.__class__.min_remaining = 0
            elif (len(self.intersect) - len(self.solver.solution)) <= self.min_remaining:
                self.__class__.min_remaining = (len(self.intersect) - len(self.solver.solution))
                self.solver.add_solution(self.min_remaining)
            
            if test_coords:
                self.undo(test_coords[0])
        
        if len(valid) == 1:
            idx = 0
            for run_coord in self.coords:
                if run_coord not in self.solver.solution:
                    self.add_found(run_coord, valid[0][idx])
                    idx += 1

class Solver(object):
    """Controlador principal del CSP"""
    
    def __init__(self, puzzle_content):
        self.horizontal_runs = {}
        self.vertical_runs = {}
        self.unique_runs_v = []
        self.unique_runs_h = []
        self.solution = {}
        self.solutions = {}
        self.partial = {}
        self.width = 0
        self.height = 0

        vert = False
        columns = []
        lines = puzzle_content.strip().split('\n')
        
        for line_no, line in enumerate(lines):
            if len(line.strip()) == 0:
                vert = True
            else:
                cells = line.strip().split(',')
                self.width = len(cells)
                if vert:
                    if len(columns) == 0:
                        columns = [[] for _ in cells]
                    for idx, cell in enumerate(cells):
                        columns[idx].append(cell)
                else:
                    self.parse_sequence(line_no, cells, self.horizontal_runs, vert)

        if columns:
            self.height = len(columns[0])
            for idx, column in enumerate(columns):
                self.parse_sequence(idx, column, self.vertical_runs, vert)

    def add_run(self, start, length, total, run_dict, vert):
        """Agregar nueva restricción"""
        if length == 0:
            raise Exception('Error en puzzle')
        run = Run(total, length, start, vert, self)
        idx = 1 if vert else 0
        if vert:
            self.unique_runs_v.append(run)
        else:
            self.unique_runs_h.append(run)
        for _ in range(length):
            run_dict[tuple(start)] = run
            start[idx] += 1

    def parse_sequence(self, idx, cells, run_dict, vert):
        """Parsear secuencia y crear restricciones"""
        total = 0
        start = []
        length = 0
        for pitch, cell in enumerate(cells):
            if cell.isdigit():
                if int(cell) > 0:
                    if total != 0:
                        self.add_run(start, length, total, run_dict, vert)
                    total = int(cell)
                    length = 0
                    start = [idx, pitch + 1] if vert else [pitch + 1, idx]
                elif int(cell) == 0:
                    length += 1
        if total != 0:
            self.add_run(start, length, total, run_dict, vert)

    def add_solution(self, remaining=0):
        """Agregar solución encontrada"""
        new_solution = False
        m = hashlib.md5()
        m.update(str(sorted(self.solution.values())).encode('utf-8'))
        if m.hexdigest() not in self.solutions:
            if remaining > 0:
                self.partial[m.hexdigest()] = remaining
            self.solutions[m.hexdigest()] = self.solution.copy()
            new_solution = True
        return new_solution

    def solve(self):
        """Algoritmo principal de resolución CSP"""
        iterations = 0
        current_filled = 1
        limit = 2
        
        print(f"🔍 Iniciando CSP - Variables: {len(self.horizontal_runs)}")
        print(f"📏 Tablero: {self.width}x{self.height}")
        
        while len(self.solution) < len(self.horizontal_runs) and iterations < 45:
            all_tested = True
            iterations += 1
            last_filled = current_filled
            current_filled = 0
            
            for run in self.unique_runs_h + self.unique_runs_v:
                current_filled += run.fill_cells()
            
            if last_filled == 0:
                for run in self.unique_runs_h + self.unique_runs_v:
                    all_tested &= run.test_possibilities(limit)
                if all_tested:
                    if Run.min_remaining > 0:
                        for partial_solution in self.solutions:
                            if len(partial_solution) == Run.min_remaining:
                                self.solution = partial_solution
                    else:
                        break
                limit *= 2
        
        print(f"🔄 Iteraciones: {iterations}")
        
        if len(self.solution) != len(self.horizontal_runs):
            print("❌ No se encontró solución única")
        else:
            Run.min_remaining = 0
            self.add_solution()
            print("✅ ¡Solución encontrada!")
        
        self.print_solutions()

    def print_solutions(self):
        """Mostrar soluciones"""
        idx = 1
        for key in self.solutions:
            if key in self.partial and Run.min_remaining != self.partial[key]:
                continue
            print(f"\n🎯 Solución {idx}:")
            print("=" * (self.width * 2))
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) in self.solutions[key]:
                        print("%i " % self.solutions[key][(x, y)], end='')
                    elif (x, y) not in self.solutions[key] and (x, y) in self.horizontal_runs:
                        print("X ", end='')
                    else:
                        print("# ", end='')
                print()
            idx += 1

def solve_kakuro_colab(debug=False):
    """Función principal para Colab"""
    print("🧩 RESOLUTOR KAKURO CSP")
    print("=" * 40)
    print("📁 Sube tu archivo de puzzle:")
    
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="Debug: %(message)s")
    
    try:
        uploaded = files.upload()
        
        if not uploaded:
            print("❌ No se subió archivo")
            return
        
        filename = list(uploaded.keys())[0]
        content = uploaded[filename].decode('utf-8')
        
        print(f"📂 Archivo: {filename}")
        
        solver = Solver(content)
        solver.solve()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_sample():
    """Crear puzzle de ejemplo"""
    sample = """XX,XX,XX,XX,XX,XX,XX,XX
17,00,00,00,00,XX,16,00
XX,XX,XX,XX,XX,XX,07,00
XX,XX,10,00,00,XX,XX,XX
XX,XX,04,00,00,XX,XX,XX
XX,XX,XX,XX,XX,XX,16,00
24,00,00,00,00,00,11,00

XX,XX,17,XX,XX,XX,XX,XX
XX,XX,00,00,10,XX,XX,07
XX,XX,XX,XX,00,00,XX,00
15,XX,00,00,00,16,XX,10
XX,XX,00,00,00,00,XX,XX
XX,XX,07,XX,XX,XX,XX,08
XX,XX,00,00,00,00,XX,00"""
    
    with open('ejemplo_kakuro.txt', 'w') as f:
        f.write(sample)
    
    print("✅ Archivo ejemplo creado")
    files.download('ejemplo_kakuro.txt')

# Para usar, ejecuta:
# solve_kakuro_colab()          # Subir archivo
# solve_kakuro_colab(True)      # Con debug  
# create_sample()               # Crear ejemplo

print("🎮 Resolutor Kakuro CSP listo!")
print("📋 Ejecuta: solve_kakuro_colab()") 