from sat_encoding import SudokuSATSolver
from input_handling import get_sudoku_grid
from typing import List, Optional
import sys


class SudokuSolverApp:
    """
    Main class for the Sudoku solver application.
    Manages the entire workflow.
    """
    
    def __init__(self):
        """
        Application initializer. 
        (API key configured in input_handling.py)
        """
        self.solver = None
        self.current_puzzle = None
        self.solutions = None
    
    def initialize(self) -> bool:
        """
        Initializes the SAT Solver.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("\n" + "="*60)
            print("SUDOKU SAT SOLVER - INITIALIZATION")
            print("="*60)
            
            # Create the Solver instance
            self.solver = SudokuSATSolver()
            print("✓ SAT Solver initialized")
            
            return True
            
        except Exception as e:
            print(f"✗ Initialization Error: {str(e)}")
            return False
    
    def load_puzzle_from_image(self, image_path: str) -> bool:
        """
        Loads the puzzle from an image file using an external API (OCR).
        
        Args:
            image_path: Path to the Sudoku image.
        
        Returns:
            True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("LOADING PUZZLE FROM IMAGE")
        print("="*60)
        print(f"Image path: {image_path}")
        
        # Get the Sudoku grid from input_handling.py
        self.current_puzzle = get_sudoku_grid(image_path)
        
        if self.current_puzzle is None:
            print("✗ Failed to extract puzzle from image")
            return False
        
        print("\n✓ Puzzle loaded successfully!")
        self._print_sudoku_grid(self.current_puzzle)
        
        return True
    
    def load_puzzle_from_matrix(self, puzzle: List[List[int]]) -> bool:
        """
        Loads the puzzle directly from a matrix (for testing purposes).
        
        Args:
            puzzle: 9x9 Sudoku matrix.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("\n" + "="*60)
            print("LOADING PUZZLE FROM MATRIX")
            print("="*60)
            
            # Simple validation
            if not isinstance(puzzle, list) or len(puzzle) != 9:
                print("✗ Error: Puzzle must be a 9x9 matrix")
                return False
            
            for row in puzzle:
                if not isinstance(row, list) or len(row) != 9:
                    print("✗ Error: Each row must have exactly 9 columns")
                    return False
            
            self.current_puzzle = puzzle
            print("\n✓ Puzzle loaded successfully!")
            self._print_sudoku_grid(self.current_puzzle)
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False
    
    def solve_puzzle(self) -> bool:
        """
        Solves the currently loaded puzzle by encoding it to SAT and finding all solutions.
        
        Returns:
            True if solutions found, False otherwise
        """
        if self.current_puzzle is None:
            print("✗ No puzzle loaded. Please load a puzzle first.")
            return False
        
        if self.solver is None:
            print("✗ Solver not initialized. Please initialize first.")
            return False
        
        try:
            print("\n" + "="*60)
            print("SOLVING PUZZLE")
            print("="*60)
            
            # Find all possible solutions
            self.solutions = self.solver.solve_all(self.current_puzzle)
            
            if not self.solutions or len(self.solutions) == 0:
                print("\n✗ No solutions found. Puzzle is unsolvable.")
                return False
            
            print(f"\n✓ Found {len(self.solutions)} solution(s)!")
            return True
            
        except Exception as e:
            print(f"✗ Solving Error: {str(e)}")
            return False
    
    def display_solutions(self) -> None:
        """
        Displays the found solutions to the user.
        """
        if self.solutions is None or len(self.solutions) == 0:
            print("✗ No solutions to display")
            return
        
        print("\n" + "="*60)
        print("SOLUTIONS")
        print("="*60)
        
        for idx, solution in enumerate(self.solutions, 1):
            print(f"\n--- Solution #{idx} ---")
            # Note: Assuming self.solver.print_grid is defined in SudokuSATSolver
            self.solver.print_grid(solution, f"Solution #{idx}") 
    
    def _print_sudoku_grid(self, grid: List[List[int]]) -> None:
        """
        Prints the Sudoku grid in a nice console format.
        (Using a local function as print_sudoku_grid is not available here)
        """
        print("\n" + "="*37)
        for i, row in enumerate(grid):
            if i % 3 == 0 and i != 0:
                print("-" * 37)
            
            row_str = ""
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                row_str += f"{val if val != 0 else '.'} "
            
            print(f"  {row_str}")
        print("="*37)
    
    def run_from_image(self, image_path: str) -> bool:
        """
        Full workflow: from image input to solution display.
        
        Args:
            image_path: Path to the Sudoku image.
        
        Returns:
            True if successful, False otherwise
        """
        # 1. Initialize
        if not self.initialize():
            return False
        
        # 2. Load puzzle
        if not self.load_puzzle_from_image(image_path):
            return False
        
        # 3. Solve
        if not self.solve_puzzle():
            return False
        
        # 4. Display
        self.display_solutions()
        
        return True
    
    def run_from_matrix(self, puzzle: List[List[int]]) -> bool:
        """
        Full workflow: from matrix input to solution display.
        
        Args:
            puzzle: 9x9 Sudoku matrix.
        
        Returns:
            True if successful, False otherwise
        """
        # 1. Initialize
        if not self.initialize():
            return False
        
        # 2. Load puzzle
        if not self.load_puzzle_from_matrix(puzzle):
            return False
        
        # 3. Solve
        if not self.solve_puzzle():
            return False
        
        # 4. Display
        self.display_solutions()
        
        return True