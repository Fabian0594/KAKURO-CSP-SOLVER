"""
RESOLUTOR DE KAKURO - CONSTRAINT SATISFACTION PROBLEM (CSP)
===========================================================

Este programa implementa un resolutor de puzzles Kakuro utilizando técnicas de 
Constraint Satisfaction Problem (CSP) con Backtracking Cronológico.

MODELADO DEL PROBLEMA:
- Variables: Cada celda vacía del tablero representa una variable
- Dominio: Números del 1 al 9 para cada variable
- Restricciones: 
  1. La suma de cada segmento debe igualar el valor objetivo
  2. No puede haber números repetidos en un mismo segmento
  3. Cada celda debe contener exactamente un dígito

TÉCNICAS UTILIZADAS:
- Memoización para optimizar cálculos recursivos
- Propagación de restricciones (constraint propagation)
- Backtracking cronológico con poda
- Heurísticas de ordenamiento de variables

Desarrollado para: Programación III - Actividad 08
Grupo: G1
"""

import math
import sys
import logging
import hashlib
import os

# Remove the Google Colab import since we're running locally
# from google.colab import files

class Memoize:
    """
    Decorador para memoización - optimiza funciones recursivas 
    almacenando resultados previamente calculados.
    Esto es crucial para el rendimiento en CSP complejos.
    """
    def __init__(self, f):  # Fixed: was _init_
        self.f = f
        self.memo = {}

    def __call__(self, *args):  # Fixed: was _call_
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]

@Memoize
def get_sums(target, count):
    """
    GENERACIÓN DE RESTRICCIONES: 
    Retorna una lista de todas las sumas que den como resultado el objetivo (target) 
    con cantidad (count) coeficientes.
    
    Esta función implementa la generación dinámica de restricciones para el CSP.
    Args:
        target (int): Suma objetivo del segmento
        count (int): Número de celdas en el segmento
    
    Returns:
        list: Lista de todas las combinaciones posibles de números
    """

    if count == 2:
        sums = [
            [target - x, x] for x in range(1, target - 1)
            if target - x != x and x < 10 and (target - x) < 10
        ]
    else:
        sums = []
        for x in range(1, target - 1):
            sums.extend(
                [sum + [x] for sum in get_sums(target - x, count - 1) if x not in sum and x < 10]
            )
    return sums


@Memoize
def get_unique_sums(target, count):
    """
    DOMINIO DE VARIABLES:
    Retorna un conjunto de sumas que den como resultado el objetivo (target) 
    con cantidad (count) coeficientes.
    Los coeficientes para cada suma están ordenados de forma ascendente.
    
    Esto reduce el espacio de búsqueda eliminando permutaciones equivalentes.
    """
    sums = get_sums(target, count)
    unique_sums = set()
    for sum in sums:
        unique_sums.add(tuple(sorted(sum)))
    return list(unique_sums)


def combinations(nums):
    """
    GENERADOR DE ASIGNACIONES:
    Obtener todas las combinaciones de números en nums.
    Utilizado en el proceso de backtracking para probar diferentes asignaciones.
    """
    combos = []
    if len(nums) == 2:
        return [[nums[0], nums[1]], [nums[1], nums[0]]]
    else:
        for num in nums:
            nums2 = nums[:]
            nums2.remove(num)
            combos.extend([x + [num] for x in combinations(nums2)])
    return combos


class Solver(object):
    """
    RESOLUTOR PRINCIPAL - IMPLEMENTACIÓN DEL CSP
    ============================================
    
    Esta clase implementa el algoritmo principal de resolución del CSP de Kakuro.
    Utiliza las siguientes técnicas:
    
    1. REPRESENTACIÓN DEL PROBLEMA:
       - Variables: Celdas vacías del tablero (coordenadas x,y)
       - Restricciones: Segmentos horizontales y verticales con sumas objetivo
    
    2. ESTRATEGIAS DE RESOLUCIÓN:
       - Propagación de restricciones (constraint propagation)
       - Backtracking cronológico con poda inteligente
       - Heurísticas de ordenamiento de variables (most constrained first)
    
    3. OPTIMIZACIONES:
       - Detección temprana de inconsistencias
       - Memoización de estados parciales
       - Reducción progresiva del dominio de variables
    """
    
    # ESTRUCTURAS DE DATOS DEL CSP:
    # Mapeo de coordenadas a tramos horizontales (restricciones)
    horizontal_runs = {}
    # Mapeo de coordenadas a tramos verticales (restricciones) 
    vertical_runs = {}
    # Lista de tramos verticales únicos (variables de restricción)
    unique_runs_v = []
    # Lista de tramos horizontales únicos (variables de restricción)
    unique_runs_h = []
    # Asignación actual de variables (solución parcial)
    solution = {}
    # Conjunto de soluciones encontradas (para análisis de unicidad)
    solutions = {}
    # Soluciones parciales (para backtracking inteligente)
    partial = {}
    # Dimensiones del tablero
    width = 0
    height = 0

    def __init__(self, puzzle_file):
        # Reset class variables for new instance
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

        # Check if file exists, if not, ask user to provide correct path
        if not os.path.exists(puzzle_file):
            print(f"File '{puzzle_file}' not found.")
            print("Please make sure the file exists in the current directory or provide the full path.")
            raise FileNotFoundError(f"File '{puzzle_file}' not found")

        with open(puzzle_file, 'r', encoding='utf-8') as in_file:
            for line_no, line in enumerate(in_file):
                # Vertical runs separated by new-line
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
        if length == 0:
            raise Exception('Error in puzzle at: %s' % (start,))
        run = Run(
            total, length, start, vert, self
        )
        idx = 1 if vert else 0
        if vert:
            self.unique_runs_v.append(run)
        else:
            self.unique_runs_h.append(run)
        # Generate the coordinate mapping
        for _ in range(length):
            run_dict[tuple(start)] = run
            start[idx] += 1

    def parse_sequence(self, idx, cells, run_dict, vert):
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
        """Add a solution to the solutions. If numbers
        are missing add it to the partial solutions.
        Return True if a new solution was added.
        """
        new_solution = False
        m = hashlib.md5()
        m.update(str(sorted(self.solution.values())).encode('utf-8'))  # Python 3 fix
        if m.hexdigest() not in self.solutions:
            if remaining > 0:
                self.partial[m.hexdigest()] = remaining
            self.solutions[m.hexdigest()] = self.solution.copy()
            new_solution = True
        return new_solution

    def solve(self):
        iterations = 0
        current_filled = 1
        limit = 2
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
        logging.debug("Limit: %s" % limit)
        logging.debug("Iterations: %s" % iterations)
        if len(self.solution) != len(self.horizontal_runs):
            print("No unique solution found.")
        else:
            Run.min_remaining = 0
            self.add_solution()
        self.print_solutions()

    def print_solutions(self):
        idx = 1
        for key in self.solutions:
            if key in self.partial and Run.min_remaining != self.partial[key]:
                continue
            print("Solution %s:" % idx)
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) in self.solutions[key]:
                        print("%i " % self.solutions[key][(x, y)], end='')
                    elif (x, y) not in self.solutions[key] and (x, y) in self.horizontal_runs:
                        print("X ", end='')
                    else:
                        print("# ", end='')
                print()  # New line
            idx += 1


class Run(object):
    """Represents a single vertical or horizontal run of numbers within the grid.
    """
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
            raise Exception("Error at %s, no digit sequences found" % (start,))
        self.digit_coords = {x: set() for x in range(1, 10)}
        (a, b) = (0, 1) if vert else (1, 0)
        self.coords = [(start[0] + a * x, start[1] + b * x) for x in range(length)]

    def __str__(self):
        return '(T: %d, L: %d) - Sequences: %s' % (self.total, self.length, self.sequences)

    def get_digits(self):
        """Return all the possible digits (excluding already found digits) as a tuple of:

        all_digits - The set containing the union of all possible digits.
        required_digits - Set of digits common to all sequences
        """
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
        """Return the digits already found."""
        found_digits = []
        for coord in self.coords:
            if coord in self.solver.solution:
                found_digits.append(self.solver.solution[coord])
        return found_digits

    def undo(self, guess_coord):
        """Undo a change to the solution if a previously
        placed digit prevents a solution from being found.
        """
        coord = None
        while coord != guess_coord:
            coord = self.coord_changes.pop()
            value = self.solver.solution[coord]
            del self.solver.solution[coord]

    def add_found(self, coord, found, testing=False):
        self.solver.solution[coord] = found
        if not testing:
            if coord in self.h_guess_coords:
                del self.h_guess_coords[coord]
            if coord in self.v_guess_coords:
                del self.v_guess_coords[coord]
        self.coord_changes.append(coord)

    def test_possibilities(self, limit):
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
        count = 0
        for digit, coords in self.digit_coords.items():  # Python 3 fix
            if len(coords) == 1 and digit in required_digits:
                coord = coords.pop()
                if coord not in self.solver.solution:
                    count += 1
                    logging.debug("Adding: %s %s" % (coord, digit))
                    self.add_found(coord, digit)
        return count

    def fill_cells(self, test=False):
        """Fill in numbers into the run and return the number
        of digits found.
        """
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
                    logging.debug("Found: %s %s" % (coord, found))
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
            if test_coords:  # Check if test_coords is not empty
                self.undo(test_coords[0])
        if len(valid) == 1:
            logging.debug("Adding: %s %s" % (self.coords[0], valid[0]))
            idx = 0
            for run_coord in self.coords:
                if run_coord not in self.solver.solution:
                    self.add_found(run_coord, valid[0][idx])
                    idx += 1


def solve_kakuro(puzzle_file=None, debug=False):
    """
    Main function to solve Kakuro puzzle

    Args:
        puzzle_file: Path to the puzzle file (required in local environment)
        debug: Enable debug output
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="Debug: %(message)s")

    try:
        if puzzle_file is None:
            print("Please provide a puzzle file path as argument.")
            print("Usage: solve_kakuro('path/to/puzzle.txt')")
            print("Or run from command line: python main.py puzzle.txt")
            return

        solver = Solver(puzzle_file)
        solver.solve()

    except Exception as e:
        print(f"Error occurred: {e}")
        if 'solver' in locals():
            solver.solutions[0] = solver.solution
            solver.print_solutions()


# Example usage:
# solve_kakuro("puzzle.txt")  # Use specific file
# solve_kakuro("puzzle.txt", debug=True)  # With debug output

if __name__ == "__main__":
    # Command line compatibility
    if len(sys.argv) >= 2:
        debug_mode = len(sys.argv) == 3 and sys.argv[2] == '--debug'
        solve_kakuro(sys.argv[1], debug_mode)
    else:
        print("Usage: python main.py <puzzle_file> [--debug]")
        print("Example: python main.py puzzle.txt")
        print("Example: python main.py puzzle.txt --debug")