from pysat.solvers import Glucose3
from typing import List, Tuple, Optional
import numpy as np

class SudokuSATSolver:
    """
    Sudoku solver - uses Satisfiability (SAT) encoding.
    """
    
    def __init__(self):
        self.clauses = []
        self.n = 9  # Sudoku dimension (9x9)
        
    def var(self, i: int, j: int, n: int) -> int:
        """
        Converts the proposition p(i, j, n) into a unique positive integer (SAT variable).
        
        Args:
            i, j: Cell coordinates (1-9).
            n: Value in the cell (1-9).
            
        Returns:
            A unique positive integer representing the SAT variable.
        """
        return (i - 1) * 81 + (j - 1) * 9 + n
        
    def add_cell_constraints(self):
        """
        Constraint: Each cell must contain exactly one number (1-9).
        Includes 'at-least-one' and 'at-most-one' rules for each cell.
        """
        for i in range(1, 10):
            for j in range(1, 10):
                # At-least-one: The cell (i, j) must contain at least one number.
                clause = [self.var(i, j, n) for n in range(1, 10)]
                self.clauses.append(clause)
                
                # At-most-one: The cell (i, j) cannot contain two different numbers.
                for n1 in range(1, 10):
                    for n2 in range(n1 + 1, 10):
                        self.clauses.append([-self.var(i, j, n1), -self.var(i, j, n2)])

    def add_row_constraints(self):
        """
        Constraint: Each number (1-9) appears exactly once in each row.
        """
        for i in range(1, 10):
            for n in range(1, 10):
                # At-least-one in row
                clause = [self.var(i, j, n) for j in range(1, 10)]
                self.clauses.append(clause)
                
                # At-most-one in row
                for j1 in range(1, 10):
                    for j2 in range(j1 + 1, 10):
                        self.clauses.append([-self.var(i, j1, n), -self.var(i, j2, n)])

    def add_col_constraints(self):
        """
        Constraint: Each number (1-9) appears exactly once in each column.
        """
        for j in range(1, 10):
            for n in range(1, 10):
                # At-least-one in col
                clause = [self.var(i, j, n) for i in range(1, 10)]
                self.clauses.append(clause)
                
                # At-most-one in col
                for i1 in range(1, 10):
                    for i2 in range(i1 + 1, 10):
                        self.clauses.append([-self.var(i1, j, n), -self.var(i2, j, n)])

    def add_box_constraints(self):
        """
        Constraint: Each number (1-9) appears exactly once in each 3x3 subgrid.
        """
        for r in range(0, 9, 3):
            for c in range(0, 9, 3):
                for n in range(1, 10):
                    # Gather variables for the number n in the current 3x3 box
                    box_vars = []
                    for i in range(3):
                        for j in range(3):
                            # Ensure 1-based indexing for var()
                            box_vars.append(self.var(r + i + 1, c + j + 1, n))
                    
                    # At-least-one in box
                    self.clauses.append(box_vars)
                    
                    # At-most-one in box
                    for k1 in range(len(box_vars)):
                        for k2 in range(k1 + 1, len(box_vars)):
                            self.clauses.append([-box_vars[k1], -box_vars[k2]])

    def encode(self):
        """
        Generates all clauses for the Sudoku constraints.
        """
        self.clauses = [] # Reset clauses
        self.add_cell_constraints()
        self.add_row_constraints()
        self.add_col_constraints()
        self.add_box_constraints()
        return self.clauses

    def solve_all(self, clues: List[List[int]]) -> List[List[List[int]]]:
        """
        Solves the Sudoku puzzle given initial clues.
        
        Args:
            clues: 9x9 matrix where 0 represents an empty cell.
            
        Returns:
            A list of all valid solutions (each solution is a 9x9 matrix).
        """
        # 1. Generate general Sudoku rules
        self.encode()
        
        # 2. Initialize the Solver
        solver = Glucose3()
        for clause in self.clauses:
            solver.add_clause(clause)
            
        # 3. Add clues (Initial values) as unit clauses
        # FIXED: Corrected indexing. Python is 0-based, SAT logic is 1-based.
        for i in range(9):
            for j in range(9):
                val = clues[i][j]
                if val != 0:
                    # Convert 0-based (i, j) to 1-based for var() function
                    solver.add_clause([self.var(i + 1, j + 1, val)])

        solutions = []
        
        # 4. Find solutions
        while solver.solve():
            model = solver.get_model()
            if model:
                grid = self.model_to_grid(model)
                solutions.append(grid)
                
                # To find all solutions, block the current one.
                # WARNING: Blocking clauses can be slow if there are many solutions.
                # For this assignment, finding one is usually enough, but we keep the logic.
                
                # Create blocking clause: negation of the current assignment
                blocking_clause = []
                for var in model:
                    # Only block the positive variables (the assigned numbers) to reduce clause size
                    if var > 0: 
                         blocking_clause.append(-var)
                
                solver.add_clause(blocking_clause)
                
                # Optional: Limit solutions to avoid infinite loops on empty grids
                if len(solutions) >= 10:
                    break
            else:
                break
        
        solver.delete()
        return solutions
    
    def model_to_grid(self, model: List[int]) -> List[List[int]]:
        """
        Converts the SAT model (variable assignment) into a 9x9 Sudoku grid.
        """
        grid = [[0 for _ in range(9)] for _ in range(9)]
        
        for var in model:
            if var > 0:  # Only look at variables set to TRUE
                # Decode the variable back to p(i, j, n)
                # var = (i-1)*81 + (j-1)*9 + n
                var_idx = var - 1
                n = (var_idx % 9) + 1
                j = ((var_idx // 9) % 9) + 1
                i = (var_idx // 81) + 1
                
                if 1 <= i <= 9 and 1 <= j <= 9:
                    grid[i-1][j-1] = n
        
        return grid
    
    def print_grid(self, grid: List[List[int]], title: str = "Sudoku"):
        """
        Prints the Sudoku grid to the console in a formatted way.
        """
        print(f"\n{title}:")
        print("+" + "---+"*9)
        for i, row in enumerate(grid):
            print("|", end="")
            for val in row:
                print(f" {val} |", end="")
            print("\n+" + "---+"*9)

